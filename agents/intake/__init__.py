"""Intake sub-agents — convert raw user uploads into caption-rich workspace artifacts.

Each modality has its own intake agent (text/image/video/audio).  They are
**normal** sub-agents: they receive their input from InputResolver via a
``[raw_<kind>_upload]`` label that matches the placeholder caption created
by ``workspace.persist_raw_upload()``.

After running, the intake agent registers a new artifact with a rich,
caption-driven description that downstream content agents can find through
their own semantic-typed labels (``[user_instruction]`` /
``[character_reference]`` / ``[location_reference]`` / ``[style_reference]``
/ etc.).
"""
