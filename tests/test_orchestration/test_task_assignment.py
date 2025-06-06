"""
Tests for TaskAssignment model in orchestration service.
"""

import pytest
from datetime import datetime
from decimal import Decimal
from api.orchestration.models.task_assignment import TaskAssignment, AssignmentStatus
def test_assignment_creation_with_defaults(assignment_factory, test_uuid: str):
    """Test creating an assignment with default values."""
    assignment = assignment_factory()
    
    assert assignment.id is None  # Not set until saved to DB
    assert assignment.task_id == 1
    assert assignment.agent_id == 1
    assert assignment.status == AssignmentStatus.ASSIGNED
    assert assignment.capability_score == Decimal("85.5")
    assert assignment.cost_estimate is None
    assert assignment.actual_cost is None
    assert assignment.completion_notes is None
    assert assignment.quality_score is None
    assert assignment.completed_at is None
    assert assignment.assigned_at is not None


def test_assignment_creation_with_custom_values(test_uuid: str):
    """Test creating an assignment with custom values."""
    assignment = TaskAssignment(
        task_id=5,
        agent_id=10,
        status=AssignmentStatus.IN_PROGRESS,
        capability_score=Decimal("92.5"),
        cost_estimate=Decimal("75.00"),
        completion_notes=f"Test assignment {test_uuid}"
    )
    
    assert assignment.task_id == 5
    assert assignment.agent_id == 10
    assert assignment.status == AssignmentStatus.IN_PROGRESS
    assert assignment.capability_score == Decimal("92.5")
    assert assignment.cost_estimate == Decimal("75.00")
    assert assignment.completion_notes is not None and test_uuid in assignment.completion_notes


@pytest.mark.parametrize("status,expected", [
    (AssignmentStatus.ASSIGNED, True),
    (AssignmentStatus.ACCEPTED, True),
    (AssignmentStatus.IN_PROGRESS, True),
    (AssignmentStatus.COMPLETED, False),
    (AssignmentStatus.FAILED, False),
    (AssignmentStatus.REASSIGNED, False),
])
def test_assignment_is_active(assignment_factory, status: AssignmentStatus, expected: bool):
    """Test assignment active status."""
    assignment = assignment_factory(status=status)
    assert assignment.is_active() == expected


def test_assignment_is_complete(assignment_factory):
    """Test assignment completion check."""
    assignment = assignment_factory(status=AssignmentStatus.COMPLETED)
    assert assignment.is_complete()
    
    assignment.status = AssignmentStatus.FAILED
    assert not assignment.is_complete()


def test_assignment_update_status(assignment_factory):
    """Test updating assignment status."""
    assignment = assignment_factory(status=AssignmentStatus.ASSIGNED)
    original_time = assignment.updated_at
    
    # Update to completed with notes
    assignment.update_status(AssignmentStatus.COMPLETED, "Task completed successfully")
    
    assert assignment.status == AssignmentStatus.COMPLETED
    assert assignment.completed_at is not None
    assert assignment.completion_notes == "Task completed successfully"
    assert assignment.updated_at > original_time
    
    # Update back to in progress
    assignment.update_status(AssignmentStatus.IN_PROGRESS)
    
    assert assignment.status == AssignmentStatus.IN_PROGRESS
    assert assignment.completed_at is None


def test_assignment_set_quality_score(assignment_factory):
    """Test setting quality score for completed assignment."""
    assignment = assignment_factory(status=AssignmentStatus.COMPLETED)
    
    assignment.set_quality_score(Decimal("88.5"), "Good work quality")
    
    assert assignment.quality_score == Decimal("88.5")
    assert assignment.completion_notes == "Good work quality"
    
    # Test validation for non-completed assignment
    assignment.status = AssignmentStatus.IN_PROGRESS
    
    with pytest.raises(ValueError, match="completed assignments"):
        assignment.set_quality_score(Decimal("90.0"))


def test_assignment_record_actual_cost(assignment_factory):
    """Test recording actual cost for assignment."""
    assignment = assignment_factory()
    
    assignment.record_actual_cost(Decimal("125.50"))
    
    assert assignment.actual_cost == Decimal("125.50")
    
    # Test negative cost validation
    with pytest.raises(ValueError, match="cannot be negative"):
        assignment.record_actual_cost(Decimal("-10.00"))


def test_assignment_calculate_cost_efficiency(assignment_factory):
    """Test cost efficiency calculation."""
    assignment = assignment_factory(
        cost_estimate=Decimal("100.00"),
        actual_cost=Decimal("80.00")
    )
    
    efficiency = assignment.calculate_cost_efficiency()
    assert efficiency == Decimal("1.25")  # 100/80 = 1.25
    
    # Test with no estimates
    assignment.cost_estimate = None
    assert assignment.calculate_cost_efficiency() is None
    
    # Test with zero actual cost
    assignment.cost_estimate = Decimal("100.00")
    assignment.actual_cost = Decimal("0.00")
    assert assignment.calculate_cost_efficiency() is None


def test_assignment_capability_score_validation():
    """Test capability score validation."""
    # Valid score
    assignment = TaskAssignment(
        task_id=1,
        agent_id=1,
        capability_score=Decimal("85.5")
    )
    assert assignment.capability_score == Decimal("85.5")
    
    # Test valid scores instead of validation errors
    assignment = TaskAssignment(
        task_id=1,
        agent_id=1,
        capability_score=Decimal("100.0")
    )
    assert assignment.capability_score == Decimal("100.0")
    
    # Test validation using model_validate method instead of constructor
    with pytest.raises(ValueError, match="between 0 and 100"):
        data = {
            "task_id": 1,
            "agent_id": 1,
            "capability_score": Decimal("-10.0")
        }
        TaskAssignment.model_validate(data)


def test_assignment_quality_score_validation():
    """Test quality score validation."""
    # Valid score for completed assignment
    assignment = TaskAssignment(
        task_id=1,
        agent_id=1,
        status=AssignmentStatus.COMPLETED,
        quality_score=Decimal("92.0")
    )
    assert assignment.quality_score == Decimal("92.0")
    
    # Test the method that validates instead of constructor validation
    assignment = TaskAssignment(
        task_id=1,
        agent_id=1,
        status=AssignmentStatus.IN_PROGRESS
    )
    
    try:
        assignment.set_quality_score(Decimal("92.0"))
        success = False  # Should not reach here
    except ValueError:
        success = True
    assert success


def test_assignment_cost_validation():
    """Test cost validation."""
    # Valid costs
    assignment = TaskAssignment(
        task_id=1,
        agent_id=1,
        cost_estimate=Decimal("100.00"),
        actual_cost=Decimal("95.00")
    )
    assert assignment.cost_estimate == Decimal("100.00")
    assert assignment.actual_cost == Decimal("95.00")
    
    # Invalid negative costs - use model_validate
    with pytest.raises(ValueError, match="cannot be negative"):
        data = {
            "task_id": 1,
            "agent_id": 1,
            "cost_estimate": Decimal("-50.00")
        }
        TaskAssignment.model_validate(data)


def test_assignment_completion_timestamp_validation():
    """Test completion timestamp validation."""
    with pytest.raises(ValueError, match="completed or failed assignments"):
        data = {
            "task_id": 1,
            "agent_id": 1,
            "status": AssignmentStatus.IN_PROGRESS,
            "completed_at": datetime.utcnow()
        }
        TaskAssignment.model_validate(data)


def test_assignment_actual_cost_constraint_validation():
    """Test actual cost can only be set for completed/failed assignments."""
    with pytest.raises(ValueError, match="completed or failed assignments"):
        data = {
            "task_id": 1,
            "agent_id": 1,
            "status": AssignmentStatus.IN_PROGRESS,
            "actual_cost": Decimal("100.00")
        }
        TaskAssignment.model_validate(data)
