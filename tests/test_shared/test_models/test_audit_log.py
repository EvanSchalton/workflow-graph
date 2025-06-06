"""
Tests for the AuditLog model.
"""

import pytest
from datetime import datetime
from typing import Dict, Any

from api.shared.models.audit_log import (
    AuditLog,
    EntityType,
    ActorType,
    AuditAction
)


@pytest.fixture
def sample_audit_log_data(test_uuid: str) -> Dict[str, Any]:
    """Create sample audit log data for testing."""
    return {
        "entity_type": EntityType.JOB_DESCRIPTION,
        "entity_id": 123,
        "action": AuditAction.CREATE,
        "actor_type": ActorType.USER,
        "actor_id": 456,
        "old_values": None,
        "new_values": {"title": f"Software Engineer {test_uuid[:8]}"},
        "metadata_info": {"request_id": test_uuid, "ip_address": "192.168.1.1"}
    }

@pytest.fixture
def system_audit_log_data(test_uuid: str) -> Dict[str, Any]:
    """Create sample system audit log data without actor_id."""
    return {
        "entity_type": EntityType.TASK,
        "entity_id": 789,
        "action": AuditAction.EXECUTE,
        "actor_type": ActorType.SYSTEM,
        "metadata_info": {"execution_id": test_uuid, "trigger": "scheduler"}
    }


def test_audit_log_creation_with_all_fields(sample_audit_log_data: Dict[str, Any]) -> None:
    """Test creating audit log with all fields."""
    audit_log = AuditLog.model_validate(sample_audit_log_data)
    
    assert audit_log.entity_type == EntityType.JOB_DESCRIPTION
    assert audit_log.entity_id == 123
    assert audit_log.action == AuditAction.CREATE
    assert audit_log.actor_type == ActorType.USER
    assert audit_log.actor_id == 456
    assert audit_log.old_values is None
    assert audit_log.new_values == {"title": f"Software Engineer {sample_audit_log_data['metadata_info']['request_id'][:8]}"}
    assert "request_id" in audit_log.metadata_info
    assert "ip_address" in audit_log.metadata_info
    assert isinstance(audit_log.created_at, datetime)


def test_audit_log_creation_minimal_fields(system_audit_log_data: Dict[str, Any]) -> None:
    """Test creating audit log with minimal required fields."""
    audit_log = AuditLog.model_validate(system_audit_log_data)
    
    assert audit_log.entity_type == EntityType.TASK
    assert audit_log.entity_id == 789
    assert audit_log.action == AuditAction.EXECUTE
    assert audit_log.actor_type == ActorType.SYSTEM
    assert audit_log.actor_id is None
    assert audit_log.old_values is None
    assert audit_log.new_values is None
    assert len(audit_log.metadata_info) == 2
    assert isinstance(audit_log.created_at, datetime)


def test_audit_log_creation_with_constructor(test_uuid: str) -> None:
    """Test creating audit log using direct constructor."""
    audit_log = AuditLog(
        entity_type=EntityType.AGENT,
        entity_id=100,
        action=AuditAction.UPDATE,
        actor_type=ActorType.API,
        actor_id=200,
        old_values={"status": "inactive"},
        new_values={"status": "active"},
        metadata_info={"test_id": test_uuid}
    )
    
    assert audit_log.entity_type == EntityType.AGENT
    assert audit_log.entity_id == 100
    assert audit_log.action == AuditAction.UPDATE
    assert audit_log.actor_type == ActorType.API
    assert audit_log.actor_id == 200
    assert audit_log.old_values == {"status": "inactive"}
    assert audit_log.new_values == {"status": "active"}
    assert audit_log.metadata_info["test_id"] == test_uuid


def test_entity_id_validation() -> None:
    """Test entity_id validation."""
    # Positive entity_id should be valid
    audit_log = AuditLog(
        entity_type=EntityType.RESUME,
        entity_id=1,
        action=AuditAction.READ,
        actor_type=ActorType.USER
    )
    assert audit_log.entity_id == 1
    
    # Zero entity_id should raise error when using model_validate
    with pytest.raises(ValueError, match="entity_id must be positive"):
        AuditLog.model_validate({
            "entity_type": "resume",
            "entity_id": 0,
            "action": "read",
            "actor_type": "user"
        })
    
    # Negative entity_id should raise error when using model_validate
    with pytest.raises(ValueError, match="entity_id must be positive"):
        AuditLog.model_validate({
            "entity_type": "resume",
            "entity_id": -1,
            "action": "read",
            "actor_type": "user"
        })


def test_actor_id_validation() -> None:
    """Test actor_id validation."""
    # Positive actor_id should be valid
    audit_log = AuditLog(
        entity_type=EntityType.TASK_ASSIGNMENT,
        entity_id=1,
        action=AuditAction.ASSIGN,
        actor_type=ActorType.USER,
        actor_id=10
    )
    assert audit_log.actor_id == 10
    
    # None actor_id should be valid
    audit_log = AuditLog(
        entity_type=EntityType.EXECUTION_COST,
        entity_id=1,
        action=AuditAction.CREATE,
        actor_type=ActorType.SYSTEM,
        actor_id=None
    )
    assert audit_log.actor_id is None
    
    # Zero actor_id should raise error when using model_validate
    with pytest.raises(ValueError, match="actor_id must be positive when provided"):
        AuditLog.model_validate({
            "entity_type": "task_assignment",
            "entity_id": 1,
            "action": "assign",
            "actor_type": "user",
            "actor_id": 0
        })
    
    # Negative actor_id should raise error when using model_validate
    with pytest.raises(ValueError, match="actor_id must be positive when provided"):
        AuditLog.model_validate({
            "entity_type": "task_assignment",
            "entity_id": 1,
            "action": "assign",
            "actor_type": "user",
            "actor_id": -5
        })


def test_metadata_info_validation() -> None:
    """Test metadata_info validation."""
    # Valid dictionary metadata_info
    audit_log = AuditLog(
        entity_type=EntityType.MODEL_CATALOG,
        entity_id=1,
        action=AuditAction.ACTIVATE,
        actor_type=ActorType.SYSTEM,
        metadata_info={"reason": "performance_improvement"}
    )
    assert audit_log.metadata_info == {"reason": "performance_improvement"}
    
    # Empty dictionary should be valid
    audit_log = AuditLog(
        entity_type=EntityType.MODEL_CATALOG,
        entity_id=1,
        action=AuditAction.ACTIVATE,
        actor_type=ActorType.SYSTEM,
        metadata_info={}
    )
    assert audit_log.metadata_info == {}
    
    # Default metadata_info should be empty dict
    audit_log = AuditLog(
        entity_type=EntityType.MODEL_CATALOG,
        entity_id=1,
        action=AuditAction.ACTIVATE,
        actor_type=ActorType.SYSTEM
    )
    assert audit_log.metadata_info == {}


@pytest.mark.parametrize("entity_type", [
    EntityType.JOB_DESCRIPTION,
    EntityType.RESUME,
    EntityType.JOB_APPLICATION,
    EntityType.AGENT,
    EntityType.TASK,
    EntityType.TASK_ASSIGNMENT,
    EntityType.MODEL_CATALOG,
    EntityType.EXECUTION_COST,
    EntityType.TASK_PROMPT,
    EntityType.RESUME_PROMPT
])
def test_all_entity_types(entity_type: EntityType) -> None:
    """Test that all entity types are valid."""
    audit_log = AuditLog(
        entity_type=entity_type,
        entity_id=1,
        action=AuditAction.CREATE,
        actor_type=ActorType.SYSTEM
    )
    assert audit_log.entity_type == entity_type


@pytest.mark.parametrize("actor_type", [
    ActorType.SYSTEM,
    ActorType.USER,
    ActorType.AGENT,
    ActorType.API,
    ActorType.SCHEDULER,
    ActorType.WEBHOOK
])
def test_all_actor_types(actor_type: ActorType) -> None:
    """Test that all actor types are valid."""
    audit_log = AuditLog(
        entity_type=EntityType.TASK,
        entity_id=1,
        action=AuditAction.UPDATE,
        actor_type=actor_type
    )
    assert audit_log.actor_type == actor_type


@pytest.mark.parametrize("action", [
    AuditAction.CREATE,
    AuditAction.UPDATE,
    AuditAction.DELETE,
    AuditAction.READ,
    AuditAction.EXECUTE,
    AuditAction.ASSIGN,
    AuditAction.UNASSIGN,
    AuditAction.ACTIVATE,
    AuditAction.DEACTIVATE,
    AuditAction.APPROVE,
    AuditAction.REJECT,
    AuditAction.COMPLETE,
    AuditAction.FAIL
])
def test_all_audit_actions(action: AuditAction) -> None:
    """Test that all audit actions are valid."""
    audit_log = AuditLog(
        entity_type=EntityType.AGENT,
        entity_id=1,
        action=action,
        actor_type=ActorType.SYSTEM
    )
    assert audit_log.action == action


def test_audit_log_str_representation(sample_audit_log_data: Dict[str, Any]) -> None:
    """Test string representation of audit log."""
    audit_log = AuditLog.model_validate(sample_audit_log_data)
    str_repr = str(audit_log)
    
    assert "CREATE job_description:123" in str_repr
    assert "by user:456" in str_repr
    assert "at" in str_repr


def test_audit_log_str_without_actor_id(system_audit_log_data: Dict[str, Any]) -> None:
    """Test string representation without actor_id."""
    audit_log = AuditLog.model_validate(system_audit_log_data)
    str_repr = str(audit_log)
    
    assert "EXECUTE task:789" in str_repr
    assert "by system" in str_repr
    assert ":None" not in str_repr


def test_audit_log_repr_representation(sample_audit_log_data: Dict[str, Any]) -> None:
    """Test repr representation of audit log."""
    audit_log = AuditLog.model_validate(sample_audit_log_data)
    repr_str = repr(audit_log)
    
    assert "AuditLog(" in repr_str
    assert "entity_type='job_description'" in repr_str
    assert "entity_id=123" in repr_str
    assert "action='create'" in repr_str
    assert "actor_type='user'" in repr_str
    assert "actor_id=456" in repr_str


def test_audit_log_created_at_default() -> None:
    """Test that created_at is set automatically."""
    before_creation = datetime.utcnow()
    
    audit_log = AuditLog(
        entity_type=EntityType.RESUME_PROMPT,
        entity_id=1,
        action=AuditAction.DELETE,
        actor_type=ActorType.USER,
        actor_id=99
    )
    
    after_creation = datetime.utcnow()
    
    assert before_creation <= audit_log.created_at <= after_creation


def test_audit_log_with_complex_values(test_uuid: str) -> None:
    """Test audit log with complex old_values and new_values."""
    old_values = {
        "title": "Old Title",
        "skills": ["Python", "SQL"],
        "config": {"enabled": False, "timeout": 30}
    }
    new_values = {
        "title": f"New Title {test_uuid[:8]}",
        "skills": ["Python", "SQL", "FastAPI"],
        "config": {"enabled": True, "timeout": 60}
    }
    
    audit_log = AuditLog(
        entity_type=EntityType.JOB_DESCRIPTION,
        entity_id=42,
        action=AuditAction.UPDATE,
        actor_type=ActorType.API,
        actor_id=1001,
        old_values=old_values,
        new_values=new_values,
        metadata_info={"change_reason": f"Enhancement request {test_uuid}"}
    )
    
    assert audit_log.old_values == old_values
    assert audit_log.new_values == new_values
    assert audit_log.metadata_info["change_reason"] == f"Enhancement request {test_uuid}"


def test_enum_string_conversion() -> None:
    """Test that enum values work with string inputs."""
    # Test with string values in model_validate
    audit_log = AuditLog.model_validate({
        "entity_type": "agent",
        "entity_id": 1,
        "action": "complete",
        "actor_type": "webhook"
    })
    
    assert audit_log.entity_type == EntityType.AGENT
    assert audit_log.action == AuditAction.COMPLETE
    assert audit_log.actor_type == ActorType.WEBHOOK
