"""
Tests for the JobApplication model.
"""

import pytest
from datetime import datetime
from typing import Dict, Any, TYPE_CHECKING

# Test import coverage for TYPE_CHECKING block
if TYPE_CHECKING:
    from api.hr.models.job_description import JobDescription
    from api.hr.models.resume import Resume

from api.hr.models.job_application import (
    JobApplication,
    JobApplicationCreate,
    JobApplicationUpdate,
    JobApplicationRead
)


@pytest.fixture
def sample_job_application_data(test_uuid: str) -> Dict[str, Any]:
    """Create sample job application data for testing."""
    return {
        "job_description_id": 1,
        "resume_id": 2,
        "status": "applied",
        "interview_notes": f"Good candidate {test_uuid[:8]}",
        "hiring_decision_reason": None
    }


def test_job_application_status_validation(test_uuid: str) -> None:
    """Test custom status validation logic."""
    # Invalid status should raise error
    with pytest.raises(ValueError, match="Status must be one of"):
        JobApplication.model_validate({
            "job_description_id": 1,
            "resume_id": 2,
            "status": "invalid_status"
        })
    
    # Valid status should work
    for valid_status in ["applied", "interviewing", "hired", "rejected"]:
        application = JobApplication.model_validate({
            "job_description_id": 1,
            "resume_id": 2,
            "status": valid_status
        })
        assert application.status == valid_status


def test_job_application_is_active_method(sample_job_application_data: Dict[str, Any]) -> None:
    """Test the is_active method business logic."""
    # Active statuses
    for status in ["applied", "interviewing"]:
        data = {**sample_job_application_data, "status": status}
        application = JobApplication.model_validate(data)
        assert application.is_active() is True
    
    # Inactive statuses
    for status in ["hired", "rejected"]:
        data = {**sample_job_application_data, "status": status}
        application = JobApplication.model_validate(data)
        assert application.is_active() is False


def test_job_application_can_transition_to_method(sample_job_application_data: Dict[str, Any]) -> None:
    """Test the can_transition_to method business logic."""
    # From 'applied' status
    application = JobApplication.model_validate({**sample_job_application_data, "status": "applied"})
    assert application.can_transition_to("interviewing") is True
    assert application.can_transition_to("rejected") is True
    assert application.can_transition_to("hired") is False
    
    # From 'interviewing' status
    application = JobApplication.model_validate({**sample_job_application_data, "status": "interviewing"})
    assert application.can_transition_to("hired") is True
    assert application.can_transition_to("rejected") is True
    assert application.can_transition_to("applied") is False
    
    # From terminal states
    for terminal_status in ["hired", "rejected"]:
        application = JobApplication.model_validate({**sample_job_application_data, "status": terminal_status})
        assert application.can_transition_to("applied") is False
        assert application.can_transition_to("interviewing") is False
        assert application.can_transition_to("hired") is False
        assert application.can_transition_to("rejected") is False


def test_job_application_update_status_method(sample_job_application_data: Dict[str, Any]) -> None:
    """Test the update_status method business logic."""
    application = JobApplication.model_validate(sample_job_application_data)
    original_updated_at = application.updated_at
    
    # Valid transition
    result = application.update_status("interviewing")
    assert result is True
    assert application.status == "interviewing"
    assert application.updated_at > original_updated_at
    
    # Invalid transition
    result = application.update_status("applied")
    assert result is False
    assert application.status == "interviewing"  # Should remain unchanged
    
    # Terminal transition with reason
    result = application.update_status("hired", "Excellent technical skills")
    assert result is True
    assert application.status == "hired"
    assert application.hiring_decision_reason == "Excellent technical skills"


def test_job_application_create_schema(sample_job_application_data: Dict[str, Any]) -> None:
    """Test the JobApplicationCreate schema validation."""
    # Remove fields not needed for create
    create_data = {k: v for k, v in sample_job_application_data.items() 
                   if k in ['job_description_id', 'resume_id', 'status', 'interview_notes']}
    
    application_create = JobApplicationCreate.model_validate(create_data)
    assert application_create.job_description_id == sample_job_application_data["job_description_id"]
    assert application_create.resume_id == sample_job_application_data["resume_id"]
    assert application_create.status == sample_job_application_data["status"]


def test_job_application_update_schema(test_uuid: str) -> None:
    """Test the JobApplicationUpdate schema validation."""
    update_data = {
        "status": "interviewing",
        "interview_notes": f"Updated notes {test_uuid[:8]}"
    }
    
    application_update = JobApplicationUpdate.model_validate(update_data)
    assert application_update.status == "interviewing"
    assert application_update.interview_notes == f"Updated notes {test_uuid[:8]}"
    assert application_update.hiring_decision_reason is None  # Should be optional


def test_job_application_read_schema(sample_job_application_data: Dict[str, Any]) -> None:
    """Test the JobApplicationRead schema validation."""
    # Add required fields for read schema
    read_data = {
        **sample_job_application_data,
        "id": 1,
        "application_date": datetime.utcnow(),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    application_read = JobApplicationRead.model_validate(read_data)
    assert application_read.id == 1
    assert application_read.job_description_id == sample_job_application_data["job_description_id"]
    assert application_read.resume_id == sample_job_application_data["resume_id"]
    assert isinstance(application_read.application_date, datetime)
    assert isinstance(application_read.created_at, datetime)
    assert isinstance(application_read.updated_at, datetime)


def test_job_application_string_representation(sample_job_application_data: Dict[str, Any]) -> None:
    """Test string representation methods."""
    application = JobApplication.model_validate({**sample_job_application_data, "id": 42})
    
    str_repr = str(application)
    assert "JobApplication(id=42" in str_repr
    assert f"job_id={sample_job_application_data['job_description_id']}" in str_repr
    assert f"resume_id={sample_job_application_data['resume_id']}" in str_repr
    assert f"status='{sample_job_application_data['status']}'" in str_repr
    
    repr_repr = repr(application)
    assert "JobApplication(id=42" in repr_repr
    assert f"job_id={sample_job_application_data['job_description_id']}" in repr_repr
    assert "application_date=" in repr_repr
