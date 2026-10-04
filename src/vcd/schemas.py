"""Data records shared by every stage. Field meanings are documented in docs/02_models_and_datasets.md."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

Source = Literal["daily_dilemmas", "moralchoice", "valueconsistency", "generated"]
Split = Literal["pilot", "train", "dev", "test", "sanity", "pool", "excluded", "unassigned"]
Variant = Literal["T0", "T1", "T2", "T3", "T4", "T5", "T6", "VC"]
Category = Literal["answer", "refusal", "insufficient", "malformed"]


class Family(BaseModel):
    """One situation with two mutually exclusive actions (or a yes/no stance item for VC)."""

    family_id: str
    source: Source
    source_id: str
    item_form: Literal["two_action", "yes_no"] = "two_action"
    topic_group: str = ""
    situation: str = ""  # second-person, declarative, trailing question removed; empty for yes_no
    question_original: str = ""  # trailing question removed from the source, or the VC question
    action_x: str  # imperative phrasing, ends with a period; "Yes" for yes_no
    action_y: str
    ambiguity: Literal["high", "low", "unknown"] = "unknown"
    controversial: Optional[bool] = None
    split: Split = "unassigned"
    needs_review: list[str] = Field(default_factory=list)
    meta: dict = Field(default_factory=dict)


class Prompt(BaseModel):
    """One concrete prompt: family x variant x option order."""

    prompt_id: str  # f"{family_id}.{variant}.o{order}"
    family_id: str
    variant: Variant
    order: Literal[1, 2]
    letter_to_action: dict[str, str]  # {"A": "x", "B": "y"} or swapped
    system: str
    user: str
    focus_action: Optional[str] = None  # "x" | "y": the positive act that T5/T6 foreground; analysis aligns the family to it


class TeacherResponse(BaseModel):
    """One model output for one prompt. `profile` rows may be truncated to the answer line."""

    prompt_id: str
    teacher: str  # key in configs/models.yaml, e.g. gpt41
    model: str
    mode: Literal["demo", "profile"]
    temperature: float
    pass_idx: int = 0
    sample_idx: int = 0
    raw: str
    category: Category
    letter: Optional[str] = None
    choice_action: Optional[str] = None  # "x" | "y"
    p_letters: Optional[dict[str, float]] = None  # renormalized over {A, B} from logprobs
    p_x: Optional[float] = None  # probability of action x from logprobs; None for sampling readout
    usage: dict = Field(default_factory=dict)
    cached: bool = False
    timestamp: str = ""
