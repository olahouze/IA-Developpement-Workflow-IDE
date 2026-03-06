"""Tests du SkillManager."""

from __future__ import annotations

from ai_workflow.managers.skill_manager import SkillManager


class TestSkillManagerBasic:
    def test_list_skills_empty(self, skill_manager: SkillManager):
        skills = skill_manager.list_skills()
        assert skills == []

    def test_write_and_get_skill(self, skill_manager: SkillManager):
        written = skill_manager.write_skill("python-style", "# Python Style Guide\n\nPEP8 rules apply.")
        assert written is True
        content = skill_manager.get_skill("python-style")
        assert content is not None
        assert "PEP8" in content

    def test_get_nonexistent_skill(self, skill_manager: SkillManager):
        assert skill_manager.get_skill("nonexistent") is None


class TestSkillManagerImmutable:
    def test_immutable_refusal(self, skill_manager: SkillManager):
        skill_manager.write_skill("locked", "immutable: true\n\n# Locked Skill", force=True)
        # Attempt to overwrite
        written = skill_manager.write_skill("locked", "# New content")
        assert written is False
        # Content unchanged
        assert "Locked Skill" in skill_manager.get_skill("locked")

    def test_immutable_force_override(self, skill_manager: SkillManager):
        skill_manager.write_skill("locked", "immutable: true\n\n# Locked", force=True)
        written = skill_manager.write_skill("locked", "# Forced override", force=True)
        assert written is True

    def test_not_immutable(self, skill_manager: SkillManager):
        skill_manager.write_skill("unlocked", "# Normal Skill")
        assert skill_manager.is_immutable("unlocked") is False


class TestSkillManagerOverrides:
    def test_effective_skill_with_override(self, skill_manager: SkillManager):
        skill_manager.write_skill("style", "# Base Style")
        skill_manager.profile.skill_overrides["style"] = "# Overridden Style"
        effective = skill_manager.get_effective_skill("style")
        assert effective == "# Overridden Style"

    def test_effective_skill_no_override(self, skill_manager: SkillManager):
        skill_manager.write_skill("style", "# Base Style")
        effective = skill_manager.get_effective_skill("style")
        assert effective == "# Base Style"

    def test_get_all_skills(self, skill_manager: SkillManager):
        skill_manager.write_skill("skill-a", "A")
        skill_manager.write_skill("skill-b", "B")
        all_skills = skill_manager.get_all_skills()
        assert len(all_skills) == 2


class TestSkillManagerInstructions:
    def test_write_instruction(self, skill_manager: SkillManager):
        path = skill_manager.write_instruction("arch-guide", "# Architecture Guide")
        assert path.is_file()
        assert path.name == "arch-guide.md"
