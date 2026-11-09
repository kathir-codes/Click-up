# ClickUp Backend

A task management backend inspired by ClickUp, built using **Python, FastAPI, GraphQL, SQLAlchemy, PostgreSQL, and AWS Cognito**.

The application provides workspace management, user authentication, role-based access control, member invitations, task management, task assignments, comments, tags, and activity tracking.

## 🚀 Features

### 1. Authentication and User Management
- User signup and signin using AWS Cognito.
- Email verification.
- JWT-based authentication.
- Access-token validation.
- User profile management.

### 2. Workspace Management
- Create, update, and delete workspaces.
- Manage workspace members.
- View workspace details.
- Workspace-based access control.

### 3. Role-Based Access Control (RBAC)
The application implements role-based permissions to control user access.

Supported roles:
- **Owner:** Workspace owner with administrative permissions.
- **Admin:** Manages workspace members, invitations, and tasks according to assigned permissions.
- **Member:** Performs permitted task-related operations.

Permissions are managed using a centralized permission system.

### 4. Invitation Management
- Invite users to workspaces.
- Accept or decline invitations.
- View pending invitations.
- Resend invitations.
- Cancel invitations.
- Remove workspace members.



### 5. Task Management
- Create, view, update, and delete tasks.
- Assign tasks to workspace members.
- Update task status.
- Update task priority.
- Manage task-related information.

### 6. Tags Management
- Create and update tags.
- Manage tags associated with tasks.

### 7. Comments and Activity Tracking
- Add, update, and delete task comments.
- Track task activities.
- Maintain task activity history.

## 📁 Project Structure

```text
clickup-backend/
│
├── migrations/
│   └── versions/
│
├── scripts/
│   └── seed_permissions.py
│
├── src/
│   ├── common/
│   │   ├── permissions.py
│   │   └── role_permissions.py
│   │
│   ├── core/
│   │   ├── cognito.py
│   │   ├── cognito_errors.py
│   │   ├── database.py
│   │   ├── dependencies.py
│   │   └── jwt.py
│   │
│   ├── db/
│   │
│   ├── exceptions/
│   │
│   ├── logging/
│   │
│   ├── middleware/
│   │
│   ├── models/
│   │
│   ├── modules/
│   │   ├── auth/
│   │   ├── authorization/
│   │   ├── user/
│   │   ├── workspace/
│   │   ├── invitation/
│   │   ├── task/
│   │   └── graphql_schema.py
│   │
│   └── main.py
│
├── alembic.ini
├── .env
├── .gitignore
└── README.md
```
