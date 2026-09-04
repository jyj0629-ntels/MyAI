# MyAI Documentation Index

## Version policy

- All design, implementation, and debugging updates are preserved in this directory.
- Files use versioned names in the format: `Name_vX.Y.md`
- Each version reflects a meaningful milestone.
- Existing documents are kept as historical records; new changes create a higher version.

## Current document set

- [MyAI_Architecture_Design_v1.0.md](MyAI_Architecture_Design_v1.0.md)
- [MyAI_Detailed_Design_v1.0.md](MyAI_Detailed_Design_v1.0.md)
- [MyAI_Implementation_Roadmap_v1.0.md](MyAI_Implementation_Roadmap_v1.0.md)
- [MyAI_Development_Log_v1.0.md](MyAI_Development_Log_v1.0.md)
- [MyAI_Development_Log_v1.1.md](MyAI_Development_Log_v1.1.md)
- [MyAI_Development_Log_v1.2.md](MyAI_Development_Log_v1.2.md)
- [MyAI_ChangeLog_v1.0.md](MyAI_ChangeLog_v1.0.md)
- [MyAI_ChangeLog_v1.1.md](MyAI_ChangeLog_v1.1.md)
- [MyAI_ChangeLog_v1.2.md](MyAI_ChangeLog_v1.2.md)

## Base principle

This project must preserve the current codebase structure and extend it incrementally.

- Keep FastAPI as the main application layer
- Keep SQLAlchemy as the data layer
- Keep the provider registry and orchestrator pattern
- Extend the personalization layer and workflow engine rather than replacing the base
- Prioritize simplicity, debuggability, portability, and backup/recovery
