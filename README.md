# ClickUp Backend -- Mermaid Flow Diagrams

This document collects the backend flow diagrams in one place. Each
diagram is separated so it is easier to understand, test, and update.

## 1. Main request architecture

This is the common path for a protected GraphQL request.

``` mermaid
flowchart TD
    A[User] --> B[Postman]
    B --> C[FastAPI]
    C --> D[Middleware]
    D --> E[Strawberry GraphQL]
    E --> F[JWT Validation]
    F --> G{Token valid?}
    G -- No --> H[Authentication Error]
    G -- Yes --> I[Resolver / Mutation]
    I --> J[Permission Check]
    J --> K[Service Layer]
    K --> L[SQLAlchemy]
    L --> M[(Supabase PostgreSQL)]
    M --> L
    L --> K
    K --> I
    I --> E
    E --> B
    B --> A
```

**In simple words:** FastAPI receives the request, Strawberry runs the
GraphQL operation, JWT validation identifies the user, permission checks
protect restricted actions, and the service/database layers perform the
work.

------------------------------------------------------------------------

# 2. Authentication

## 2.1 Sign up

``` mermaid
sequenceDiagram
    autonumber
    actor User
    participant Postman
    participant FastAPI
    participant GraphQL as Strawberry GraphQL
    participant Auth as Auth Mutation
    participant Cognito as AWS Cognito
    participant Email as Email Service

    User->>Postman: Enter name, email and password
    Postman->>FastAPI: signup mutation
    FastAPI->>GraphQL: Forward GraphQL request
    GraphQL->>Auth: signup()
    Auth->>Cognito: Sign up user
    Cognito-->>Auth: Signup successful
    Cognito->>Email: Send verification code
    Email-->>User: Verification email
    Auth-->>GraphQL: Signup response
    GraphQL-->>Postman: Success response
    Postman-->>User: Ask user to check email
```

## 2.2 Email verification

``` mermaid
sequenceDiagram
    autonumber
    actor User
    participant Postman
    participant FastAPI
    participant GraphQL as Strawberry GraphQL
    participant Auth as Auth Mutation
    participant Cognito as AWS Cognito

    User->>Postman: Enter email and verification code
    Postman->>FastAPI: confirmSignup mutation
    FastAPI->>GraphQL: Forward GraphQL request
    GraphQL->>Auth: confirm_signup()
    Auth->>Cognito: Confirm sign up
    Cognito-->>Auth: Email confirmed
    Auth-->>GraphQL: Confirmation response
    GraphQL-->>Postman: Success response
    Postman-->>User: Email verified
```

## 2.3 Sign in

``` mermaid
sequenceDiagram
    autonumber
    actor User
    participant Postman
    participant FastAPI
    participant GraphQL as Strawberry GraphQL
    participant Auth as Auth Mutation
    participant Cognito as AWS Cognito

    User->>Postman: Enter email and password
    Postman->>FastAPI: signin mutation
    FastAPI->>GraphQL: Forward GraphQL request
    GraphQL->>Auth: signin()
    Auth->>Cognito: Authenticate user
    Cognito-->>Auth: Return tokens
    Auth-->>GraphQL: Return token response
    GraphQL-->>Postman: Token response
    Postman-->>User: Sign in successful
```

## 2.4 Validate access token for a protected request

``` mermaid
sequenceDiagram
    autonumber

    actor User
    participant Postman
    participant FastAPI
    participant GraphQL as Strawberry GraphQL
    participant JWT as JWT Validation
    participant Cognito as AWS Cognito
    participant DB as SQLAlchemy
    participant PG as Supabase PostgreSQL

    User->>Postman: Request user profile
    Postman->>FastAPI: getMyProfile query + access token
    FastAPI->>GraphQL: Forward request
    GraphQL->>JWT: Validate access token
    JWT->>Cognito: Get public signing keys (JWKS)
    Cognito-->>JWT: Return public keys
    JWT->>JWT: Verify signature and token claims

    alt Token is valid
        JWT-->>GraphQL: Return authenticated user (sub)
        GraphQL->>DB: Get user profile
        DB->>PG: SELECT user profile using cognito_sub
        PG-->>DB: User record
        DB-->>GraphQL: Return user profile
        GraphQL-->>Postman: Profile response
        Postman-->>User: Display user profile
    else Token is invalid
        JWT-->>GraphQL: Authentication error
        GraphQL-->>Postman: Unauthorized response
        Postman-->>User: Display authentication error
    end
```

**Important:** Cognito handles user identity and tokens. Supabase
PostgreSQL stores the application's user profile and workspace/task
data.

------------------------------------------------------------------------

# 3. Workspace

## 3.1 Create workspace

``` mermaid
sequenceDiagram
    autonumber
    actor User
    participant Postman
    participant FastAPI
    participant GraphQL as Strawberry GraphQL
    participant JWT as JWT Validation
    participant Service as Workspace Service
    participant Validator as Pydantic Validation
    participant DB as SQLAlchemy
    participant PG as Supabase PostgreSQL

    User->>Postman: Enter workspace name and description
    Postman->>FastAPI: createWorkspace mutation + access token
    FastAPI->>GraphQL: Forward request
    GraphQL->>JWT: Validate access token
    JWT-->>GraphQL: Authenticated user identity
    GraphQL->>Service: create_workspace(input, user_id)
    Service->>Validator: Validate workspace input
    Validator-->>Service: Validated workspace data
    Service->>DB: Create workspace
    DB->>PG: INSERT workspace
    PG-->>DB: Workspace record
    Service->>DB: Add creator as Owner
    DB->>PG: INSERT workspace membership
    PG-->>DB: Membership record
    DB-->>Service: Workspace created
    Service-->>GraphQL: Workspace result
    GraphQL-->>Postman: Success response
    Postman-->>User: Workspace created
```
## 3.2 Get workspace details

``` mermaid
sequenceDiagram
    autonumber
    actor User
    participant Postman
    participant FastAPI
    participant GraphQL as Strawberry GraphQL
    participant JWT as JWT Validation
    participant Service as Workspace Service
    participant DB as SQLAlchemy
    participant PG as Supabase PostgreSQL

    User->>Postman: Request workspace details
    Postman->>FastAPI: workspace query + access token
    FastAPI->>GraphQL: Forward request
    GraphQL->>JWT: Validate access token
    JWT-->>GraphQL: Authenticated user identity
    GraphQL->>Service: get_workspace(workspace_id, user_id)
    Service->>DB: Check workspace membership
    DB->>PG: SELECT workspace membership
    PG-->>DB: Membership result
    DB-->>Service: Membership result

    alt User is a workspace member
        Service->>DB: Get workspace details
        DB->>PG: SELECT workspace
        PG-->>DB: Workspace record
        DB-->>Service: Workspace details
        Service-->>GraphQL: Workspace details
        GraphQL-->>Postman: Workspace response
    else User is not a workspace member
        Service-->>GraphQL: Access denied
        GraphQL-->>Postman: Authorization error
    end
```

## 3.3 Update workspace

``` mermaid
sequenceDiagram
    autonumber
    actor User
    participant Postman
    participant FastAPI
    participant GraphQL as Strawberry GraphQL
    participant JWT as JWT Validation
    participant RBAC as Permission Check
    participant Service as Workspace Service
    participant Validator as Pydantic Validation
    participant DB as SQLAlchemy
    participant PG as Supabase PostgreSQL

    User->>Postman: Submit updated workspace details
    Postman->>FastAPI: updateWorkspace mutation + access token
    FastAPI->>GraphQL: Forward request
    GraphQL->>JWT: Validate access token
    JWT-->>GraphQL: Authenticated user identity
    GraphQL->>RBAC: Check UPDATE_WORKSPACE permission
    RBAC->>DB: Check workspace permission
    DB->>PG: Read membership, role and permissions
    PG-->>DB: Permission data
    DB-->>RBAC: Permission result

    alt Permission granted
        RBAC-->>GraphQL: Access granted
        GraphQL->>Service: update_workspace(input, user_id)
        Service->>Validator: Validate update input
        Validator-->>Service: Validated data
        Service->>DB: Update workspace
        DB->>PG: UPDATE workspace
        PG-->>DB: Updated record
        DB-->>Service: Update result
        Service-->>GraphQL: Updated workspace
        GraphQL-->>Postman: Success response
    else Permission denied
        RBAC-->>GraphQL: Access denied
        GraphQL-->>Postman: Authorization error
    end
```

## 3.4 Soft-delete workspace and its tasks

The project uses soft deletion. The workspace and its task hierarchy are
marked with `deleted_at`; rows are not physically removed.

``` mermaid
sequenceDiagram
    autonumber
    actor User
    participant Postman
    participant FastAPI
    participant GraphQL as Strawberry GraphQL
    participant JWT as JWT Validation
    participant RBAC as Permission Check
    participant Service as Workspace Service
    participant DB as SQLAlchemy
    participant PG as Supabase PostgreSQL

    User->>Postman: Request workspace deletion
    Postman->>FastAPI: deleteWorkspace mutation + access token
    FastAPI->>GraphQL: Forward request
    GraphQL->>JWT: Validate access token
    JWT-->>GraphQL: Authenticated user identity
    GraphQL->>RBAC: Check DELETE_WORKSPACE permission
    RBAC->>DB: Check workspace permission
    DB->>PG: Read role and permissions
    PG-->>DB: Permission data
    DB-->>RBAC: Permission result

    alt Permission granted
        RBAC-->>GraphQL: Access granted
        GraphQL->>Service: delete_workspace(workspace_id)
        Service->>DB: Fetch workspace and related tasks
        DB->>PG: SELECT workspace and task hierarchy
        PG-->>DB: Workspace and task records
        DB-->>Service: Related records
        Service->>Service: Set deleted_at on workspace
        Service->>Service: Set deleted_at on tasks and nested subtasks
        Service->>Service: Set deleted_at on related comments, if supported
        Service->>DB: Save all soft-delete changes in one transaction
        DB->>PG: UPDATE affected rows SET deleted_at
        PG-->>DB: Changes saved
        DB-->>Service: Transaction successful
        Service-->>GraphQL: Deletion result
        GraphQL-->>Postman: Success response
        Postman-->>User: Workspace deleted
    else Permission denied
        RBAC-->>GraphQL: Access denied
        GraphQL-->>Postman: Authorization error
    end
```

**Rule:** `deleted_at IS NULL` means active. A non-null `deleted_at`
means deleted. Keep task activity history as an audit trail.

------------------------------------------------------------------------

# 4. Invitations

## 4.1 Create invitation

``` mermaid
sequenceDiagram
    autonumber
    actor User
    actor Invitee
    participant Postman
    participant FastAPI
    participant GraphQL as Strawberry GraphQL
    participant JWT as JWT Validation
    participant RBAC as Permission Check
    participant Service as Invitation Service
    participant Validator as Pydantic Validation
    participant DB as SQLAlchemy
    participant PG as Supabase PostgreSQL

    User->>Postman: Enter invitee email, workspace ID and role
    Postman->>FastAPI: createInvitation mutation + access token
    FastAPI->>GraphQL: Forward request
    GraphQL->>JWT: Validate access token
    JWT-->>GraphQL: Authenticated user identity
    GraphQL->>RBAC: Check INVITE_MEMBER permission
    RBAC->>DB: Check workspace permission
    DB->>PG: Read role and permissions
    PG-->>DB: Permission records
    DB-->>RBAC: Permission result

    alt User has INVITE_MEMBER permission
        RBAC-->>GraphQL: Permission granted
        GraphQL->>Service: create_invitation(input, user_id)
        Service->>Validator: Validate invitation input
        Validator-->>Service: Validated invitation data
        Service->>Service: Generate invitation token
        Service->>DB: Create pending invitation
        DB->>PG: INSERT invitation with PENDING status
        PG-->>DB: Invitation record
        DB-->>Service: Invitation created
        Service-->>GraphQL: Invitation details and token
        GraphQL-->>Postman: Invitation response
        Postman-->>User: Display invitation token
        User->>Invitee: Share invitation token
    else Permission denied
        RBAC-->>GraphQL: Permission denied
        GraphQL-->>Postman: Authorization error
    end
```

## 4.2 Get workspace invitations

``` mermaid
sequenceDiagram
    autonumber
    actor User
    participant Postman
    participant FastAPI
    participant GraphQL as Strawberry GraphQL
    participant JWT as JWT Validation
    participant RBAC as Permission Check
    participant Service as Invitation Service
    participant DB as SQLAlchemy
    participant PG as Supabase PostgreSQL

    User->>Postman: Request workspace invitations
    Postman->>FastAPI: workspaceInvitations query + access token
    FastAPI->>GraphQL: Forward request
    GraphQL->>JWT: Validate access token
    JWT-->>GraphQL: Authenticated user identity
    GraphQL->>RBAC: Check VIEW_INVITATION permission
    RBAC->>DB: Check workspace permission
    DB->>PG: Read role and permissions
    PG-->>DB: Permission records
    DB-->>RBAC: Permission result

    alt Permission granted
        RBAC-->>GraphQL: Access granted
        GraphQL->>Service: get_workspace_invitations(workspace_id)
        Service->>DB: Fetch workspace invitations
        DB->>PG: SELECT invitations
        PG-->>DB: Invitation records
        DB-->>Service: Invitation list
        Service-->>GraphQL: Invitation list
        GraphQL-->>Postman: Invitations response
    else Permission denied
        RBAC-->>GraphQL: Access denied
        GraphQL-->>Postman: Authorization error
    end
```

## 4.3 Accept invitation

``` mermaid
sequenceDiagram
    autonumber
    actor Invitee
    participant Postman
    participant FastAPI
    participant GraphQL as Strawberry GraphQL
    participant JWT as JWT Validation
    participant Service as Invitation Service
    participant DB as SQLAlchemy
    participant PG as Supabase PostgreSQL

    Invitee->>Postman: Submit invitation token
    Postman->>FastAPI: acceptInvitation mutation + access token
    FastAPI->>GraphQL: Forward request
    GraphQL->>JWT: Validate access token
    JWT-->>GraphQL: Authenticated user identity
    GraphQL->>Service: accept_invitation(token, user_id)
    Service->>DB: Find invitation by token
    DB->>PG: SELECT invitation by token
    PG-->>DB: Invitation record
    DB-->>Service: Invitation details
    Service->>Service: Check status is PENDING
    Service->>Service: Check invited email matches user
    Service->>Service: Check invitation has not expired

    alt Invitation is valid
        Service->>DB: Add user to workspace with invited role
        DB->>PG: INSERT workspace member
        PG-->>DB: Membership record
        Service->>DB: Mark invitation ACCEPTED
        DB->>PG: UPDATE invitation status
        PG-->>DB: Updated invitation
        DB-->>Service: Acceptance saved
        Service-->>GraphQL: Acceptance response
        GraphQL-->>Postman: Success response
        Postman-->>Invitee: Workspace joined
    else Invitation is invalid, expired or already used
        Service-->>GraphQL: Invitation error
        GraphQL-->>Postman: Error response
    end
```

## 4.4 Cancel invitation

``` mermaid
sequenceDiagram
    autonumber
    actor User
    participant Postman
    participant FastAPI
    participant GraphQL as Strawberry GraphQL
    participant JWT as JWT Validation
    participant RBAC as Permission Check
    participant Service as Invitation Service
    participant DB as SQLAlchemy
    participant PG as Supabase PostgreSQL

    User->>Postman: Submit invitation ID
    Postman->>FastAPI: cancelInvitation mutation + access token
    FastAPI->>GraphQL: Forward request
    GraphQL->>JWT: Validate access token
    JWT-->>GraphQL: Authenticated user identity
    GraphQL->>RBAC: Check CANCEL_INVITATION permission
    RBAC->>DB: Check workspace permission
    DB->>PG: Read role and permissions
    PG-->>DB: Permission records
    DB-->>RBAC: Permission result

    alt Permission granted
        RBAC-->>GraphQL: Access granted
        GraphQL->>Service: cancel_invitation(invitation_id)
        Service->>DB: Fetch invitation and check status
        DB->>PG: SELECT invitation
        PG-->>DB: Invitation record
        DB-->>Service: Invitation details
        Service->>DB: Set status to CANCELLED
        DB->>PG: UPDATE invitation
        PG-->>DB: Updated invitation
        DB-->>Service: Cancellation saved
        Service-->>GraphQL: Cancellation response
        GraphQL-->>Postman: Success response
    else Permission denied
        RBAC-->>GraphQL: Access denied
        GraphQL-->>Postman: Authorization error
    end
```

------------------------------------------------------------------------

# 5. Tasks and subtasks

## 5.1 Create task

``` mermaid
sequenceDiagram
    autonumber
    actor User
    participant Postman
    participant FastAPI
    participant GraphQL as Strawberry GraphQL
    participant JWT as JWT Validation
    participant RBAC as Permission Check
    participant Validator as Pydantic Validation
    participant Service as Task Service
    participant Activity as Activity Service
    participant DB as SQLAlchemy
    participant PG as Supabase PostgreSQL

    User->>Postman: Send createTask mutation
    Postman->>FastAPI: POST /graphql + access token
    FastAPI->>GraphQL: Forward request
    GraphQL->>JWT: Validate access token
    JWT-->>GraphQL: Authenticated user identity
    GraphQL->>RBAC: Check CREATE_TASK permission
    RBAC->>DB: Check workspace membership and permission
    DB->>PG: Read role and permissions
    PG-->>DB: Permission records
    DB-->>RBAC: Permission result

    alt Permission granted
        RBAC-->>GraphQL: Access granted
        GraphQL->>Validator: Validate task input
        Validator-->>GraphQL: Validated task data
        GraphQL->>Service: create_task()
        Service->>Service: Check workspace is active
        Service->>DB: Insert task
        DB->>PG: INSERT task
        PG-->>DB: Created task
        DB-->>Service: Task record
        Service->>Activity: Record TASK_CREATED
        Activity->>DB: Insert activity record
        DB->>PG: INSERT task_activity
        PG-->>DB: Activity saved
        DB-->>Activity: Activity record
        Activity-->>Service: Activity recorded
        Service-->>GraphQL: Created task
        GraphQL-->>Postman: GraphQL response
        Postman-->>User: Display task
    else Permission denied
        RBAC-->>GraphQL: Access denied
        GraphQL-->>Postman: Authorization error
    end
```

## 5.2 Create subtask

``` mermaid
sequenceDiagram
    autonumber
    actor User
    participant Postman
    participant GraphQL as Strawberry GraphQL
    participant JWT as JWT Validation
    participant RBAC as Permission Check
    participant Service as Task Service
    participant DB as SQLAlchemy
    participant PG as Supabase PostgreSQL

    User->>Postman: Send createSubtask mutation
    Postman->>GraphQL: POST /graphql + access token
    GraphQL->>JWT: Validate access token
    JWT-->>GraphQL: Authenticated user
    GraphQL->>RBAC: Check CREATE_TASK permission
    RBAC->>DB: Verify permission
    DB->>PG: Read workspace permissions
    PG-->>DB: Permission records
    DB-->>RBAC: Permission result

    alt Permission granted
        RBAC-->>GraphQL: Access granted
        GraphQL->>Service: create_subtask()
        Service->>DB: Check workspace and parent task
        DB->>PG: Read workspace and parent task
        PG-->>DB: Workspace and task details
        DB-->>Service: Validation data

        alt Workspace or parent task is invalid
            Service-->>GraphQL: Return validation error
            GraphQL-->>Postman: Error response
            Postman-->>User: Display error
        else Workspace and parent task are valid
            Service->>Service: Check parent task is active and not a subtask
            Service->>DB: Create subtask and activity
            DB->>PG: INSERT subtask and task_activity
            PG-->>DB: Saved records
            DB-->>Service: Created subtask
            Service-->>GraphQL: Return created subtask
            GraphQL-->>Postman: GraphQL response
            Postman-->>User: Display created subtask
        end
    else Permission denied
        RBAC-->>GraphQL: Access denied
        GraphQL-->>Postman: Authorization error
        Postman-->>User: Display error
    end
```

**Checks have different purposes:** - Parent exists: confirms the
requested task can be found. - Parent active: prevents creating a
subtask under a deleted task. - Parent is not already a subtask:
enforces the rule that a subtask cannot have another subtask.



## 5.3 Get task details

``` mermaid
sequenceDiagram
    autonumber
    actor User
    participant Postman
    participant FastAPI
    participant GraphQL as Strawberry GraphQL
    participant JWT as JWT Validation
    participant RBAC as Permission Check
    participant Service as Task Service
    participant DB as SQLAlchemy
    participant PG as Supabase PostgreSQL

    User->>Postman: Send getTaskDetails query
    Postman->>FastAPI: POST /graphql + access token
    FastAPI->>GraphQL: Forward request
    GraphQL->>JWT: Validate access token
    JWT-->>GraphQL: Authenticated user identity
    GraphQL->>RBAC: Check VIEW_TASK permission
    RBAC->>DB: Check workspace permission
    DB->>PG: Read membership and permissions
    PG-->>DB: Permission data
    DB-->>RBAC: Permission result
    RBAC-->>GraphQL: Access granted
    GraphQL->>Service: get_task_details(task_id)
    Service->>DB: Fetch active task and related data
    DB->>PG: SELECT task, subtasks, comments and activity
    PG-->>DB: Related records
    DB-->>Service: Task details
    Service-->>GraphQL: Task details
    GraphQL-->>Postman: GraphQL response
    Postman-->>User: Display task details
```

## 5.4 Update task

``` mermaid
sequenceDiagram
    autonumber
    actor User
    participant Postman
    participant FastAPI
    participant GraphQL as Strawberry GraphQL
    participant JWT as JWT Validation
    participant RBAC as Permission Check
    participant Validator as Pydantic Validation
    participant Service as Task Service
    participant Activity as Activity Service
    participant DB as SQLAlchemy
    participant PG as Supabase PostgreSQL

    User->>Postman: Send updateTask mutation
    Postman->>FastAPI: POST /graphql + access token
    FastAPI->>GraphQL: Forward request
    GraphQL->>JWT: Validate access token
    JWT-->>GraphQL: Authenticated user identity
    GraphQL->>RBAC: Check UPDATE_TASK permission
    RBAC->>DB: Check workspace permission
    DB->>PG: Read role and permissions
    PG-->>DB: Permission data
    DB-->>RBAC: Permission result
    RBAC-->>GraphQL: Access granted
    GraphQL->>Validator: Validate update input
    Validator-->>GraphQL: Validated data
    GraphQL->>Service: update_task()
    Service->>DB: Fetch task
    DB->>PG: SELECT task
    PG-->>DB: Task record
    DB-->>Service: Task record
    Service->>Service: Check task is active
    Service->>DB: Update task fields
    DB->>PG: UPDATE task
    PG-->>DB: Updated task
    DB-->>Service: Updated record
    Service->>Activity: Record changed fields
    Activity->>DB: Insert activity records
    DB->>PG: INSERT task_activity
    PG-->>DB: Activity saved
    DB-->>Activity: Activity records
    Activity-->>Service: Activity recorded
    Service-->>GraphQL: Updated task
    GraphQL-->>Postman: GraphQL response
    Postman-->>User: Display updated task
```

## 5.5 Delete task and nested subtasks (soft delete)

``` mermaid
sequenceDiagram
    autonumber
    actor User
    participant Postman
    participant GraphQL as Strawberry GraphQL
    participant JWT as JWT Validation
    participant RBAC as Permission Check
    participant Service as Task Service
    participant DB as SQLAlchemy
    participant PG as Supabase PostgreSQL

    User->>Postman: Send deleteTask mutation
    Postman->>GraphQL: POST /graphql + access token
    GraphQL->>JWT: Validate access token
    JWT-->>GraphQL: Authenticated user
    GraphQL->>RBAC: Check DELETE_TASK permission
    RBAC-->>GraphQL: Permission result

    alt Permission granted
        GraphQL->>Service: delete_task()
        Service->>DB: Find active task
        DB->>PG: Get task
        PG-->>DB: Task details
        DB-->>Service: Task record

        alt Task not found or already deleted
            Service-->>GraphQL: Return error
        else Task is active
            Service->>DB: Find subtasks and comments
            DB->>PG: Get related records
            PG-->>DB: Related records
            DB-->>Service: Subtasks and comments
            Service->>DB: Soft-delete task, subtasks and comments
            Note over Service,PG: Set deleted_at and commit transaction
            Service-->>GraphQL: Deletion successful
        end

        GraphQL-->>Postman: GraphQL response
        Postman-->>User: Display result
    else Permission denied
        GraphQL-->>Postman: Authorization error
        Postman-->>User: Display error
    end
```



## 5.6 Assign task to workspace member

``` mermaid
sequenceDiagram
    autonumber
    actor User
    participant Postman
    participant FastAPI
    participant GraphQL as Strawberry GraphQL
    participant JWT as JWT Validation
    participant RBAC as Permission Check
    participant Validator as Pydantic Validation
    participant Service as Task Service
    participant Activity as Activity Service
    participant DB as SQLAlchemy
    participant PG as Supabase PostgreSQL

    User->>Postman: Send assignTask mutation
    Postman->>FastAPI: GraphQL mutation + access token
    FastAPI->>GraphQL: Forward request
    GraphQL->>JWT: Validate access token
    JWT-->>GraphQL: Authenticated user identity
    GraphQL->>RBAC: Check ASSIGN_TASK permission
    RBAC->>DB: Check workspace permission
    DB->>PG: Read role and permissions
    PG-->>DB: Permission data
    DB-->>RBAC: Permission result
    RBAC-->>GraphQL: Access granted
    GraphQL->>Validator: Validate assignee input
    Validator-->>GraphQL: Validated data
    GraphQL->>Service: assign_task()
    Service->>DB: Verify active task and workspace member
    DB->>PG: SELECT task and workspace membership
    PG-->>DB: Records
    DB-->>Service: Records
    Service->>DB: Update assignee_id
    DB->>PG: UPDATE task
    PG-->>DB: Updated task
    DB-->>Service: Updated task
    Service->>Activity: Record ASSIGNEE change
    Activity->>DB: Insert activity
    DB->>PG: INSERT task_activity
    PG-->>DB: Activity saved
    DB-->>Activity: Activity record
    Activity-->>Service: Activity recorded
    Service-->>GraphQL: Assigned task
    GraphQL-->>Postman: GraphQL response
    Postman-->>User: Display assigned task
```

------------------------------------------------------------------------

# 6. Task comments

## 6.1 Create comment on a task or subtask

``` mermaid
sequenceDiagram
    autonumber
    actor User
    participant Postman
    participant GraphQL as Strawberry GraphQL
    participant JWT as JWT Validation
    participant RBAC as Permission Check
    participant Service as Comment Service
    participant DB as SQLAlchemy
    participant PG as Supabase PostgreSQL

    User->>Postman: Send createComment mutation
    Postman->>GraphQL: POST /graphql + access token
    GraphQL->>JWT: Validate access token
    JWT-->>GraphQL: Authenticated user
    GraphQL->>RBAC: Check comment permission
    RBAC-->>GraphQL: Permission result

    alt Permission granted
        GraphQL->>Service: create_task_comment()
        Service->>DB: Find task or subtask
        DB->>PG: Get task
        PG-->>DB: Task details
        DB-->>Service: Task record

        alt Task not found or deleted
            Service-->>GraphQL: Return error
        else Task is active
            Service->>Service: Validate comment input
            Service->>DB: Insert comment
            DB->>PG: Save comment
            PG-->>DB: Created comment
            DB-->>Service: Comment record
            Service-->>GraphQL: Return created comment
        end

        GraphQL-->>Postman: GraphQL response
        Postman-->>User: Display result
    else Permission denied
        GraphQL-->>Postman: Authorization error
        Postman-->>User: Display error
    end
```

## 6.2 Get comments

``` mermaid
sequenceDiagram
    autonumber
    actor User
    participant Postman
    participant FastAPI
    participant GraphQL as Strawberry GraphQL
    participant JWT as JWT Validation
    participant RBAC as Permission Check
    participant Service as Comment Service
    participant DB as SQLAlchemy
    participant PG as Supabase PostgreSQL

    User->>Postman: Request task comments
    Postman->>FastAPI: getTaskComments query + access token
    FastAPI->>GraphQL: Forward request
    GraphQL->>JWT: Validate access token
    JWT-->>GraphQL: Authenticated user identity
    GraphQL->>RBAC: Check VIEW_TASK permission
    RBAC->>DB: Check workspace permission
    DB->>PG: Read membership and permissions
    PG-->>DB: Permission data
    DB-->>RBAC: Permission result
    RBAC-->>GraphQL: Access granted
    GraphQL->>Service: get_task_comments(task_id)
    Service->>DB: Find task or subtask
    DB->>PG: SELECT task
    PG-->>DB: Task record
    DB-->>Service: Task record
    Service->>Service: Check target task is active
    Service->>DB: Fetch active comments
    DB->>PG: SELECT comments WHERE deleted_at IS NULL
    PG-->>DB: Comment records
    DB-->>Service: Comments
    Service-->>GraphQL: Comment list
    GraphQL-->>Postman: GraphQL response
    Postman-->>User: Display comments
```

## 6.3 Update comment

``` mermaid
sequenceDiagram
    autonumber
    actor User
    participant Postman
    participant FastAPI
    participant Middleware
    participant GraphQL as Strawberry GraphQL
    participant JWT as JWT Validation
    participant RBAC as Permission Check
    participant Service as Service Layer
    participant DB as SQLAlchemy
    participant PG as Supabase PostgreSQL

    User->>Postman: Send GraphQL request
    Postman->>FastAPI: POST /graphql + access token
    FastAPI->>Middleware: Process request
    Middleware->>GraphQL: Forward request
    GraphQL->>JWT: Validate access token

    alt Token invalid
        JWT-->>GraphQL: Authentication error
        GraphQL-->>Postman: Return error
        Postman-->>User: Display authentication error
    else Token valid
        JWT-->>GraphQL: Return authenticated user
        GraphQL->>RBAC: Check permission

        alt Permission granted
            RBAC-->>GraphQL: Permission approved
            GraphQL->>Service: Execute resolver / mutation
            Service->>DB: Perform database operation
            DB->>PG: Execute SQL query
            PG-->>DB: Return database result
            DB-->>Service: Return result
            Service-->>GraphQL: Return operation result
            GraphQL-->>Postman: GraphQL response
            Postman-->>User: Display response
        else Permission denied
            RBAC-->>GraphQL: Authorization error
            GraphQL-->>Postman: Return error
            Postman-->>User: Display authorization error
        end
    end
```

## 6.4 Delete comment (soft delete)

``` mermaid
sequenceDiagram
    autonumber
    actor User
    participant Postman
    participant GraphQL as Strawberry GraphQL
    participant JWT as JWT Validation
    participant RBAC as Permission Check
    participant Service as Comment Service
    participant DB as SQLAlchemy
    participant PG as Supabase PostgreSQL

    User->>Postman: Send deleteComment mutation
    Postman->>GraphQL: POST /graphql + access token
    GraphQL->>JWT: Validate access token
    JWT-->>GraphQL: Authenticated user
    GraphQL->>RBAC: Check delete-comment permission
    RBAC-->>GraphQL: Permission result

    alt Permission granted
        GraphQL->>Service: delete_task_comment()
        Service->>DB: Find active task and comment
        DB->>PG: Get task and comment
        PG-->>DB: Task and comment details
        DB-->>Service: Records

        alt Task or comment is invalid
            Service-->>GraphQL: Return error
        else Task and comment are valid
            Service->>Service: Check user can delete comment
            Service->>DB: Set comment deleted_at
            DB->>PG: Update comment
            PG-->>DB: Change saved
            DB-->>Service: Deletion completed
            Service-->>GraphQL: Return deletion success
        end

        GraphQL-->>Postman: GraphQL response
        Postman-->>User: Display result
    else Permission denied
        GraphQL-->>Postman: Authorization error
        Postman-->>User: Display error
    end
```

**Note:** The comment soft-delete diagrams assume the `TaskComment`
model has a `deleted_at` column. Add a database migration if it does not
exist yet.

------------------------------------------------------------------------

# 7. Tags

A tag belongs to a workspace. Assigning a tag creates a link between a
task and a tag. Removing a tag from a task deletes only that link, not
the tag itself.

## 7.1 Create tag

``` mermaid
sequenceDiagram
    autonumber
    actor User
    participant Postman
    participant FastAPI
    participant GraphQL as Strawberry GraphQL
    participant JWT as JWT Validation
    participant RBAC as Permission Check
    participant Service as Tag Service
    participant DB as SQLAlchemy
    participant PG as Supabase PostgreSQL

    User->>Postman: Submit tag details
    Postman->>FastAPI: createTag mutation + access token
    FastAPI->>GraphQL: Forward request
    GraphQL->>JWT: Validate access token
    JWT-->>GraphQL: Authenticated user identity
    GraphQL->>RBAC: Check CREATE_TAG permission
    RBAC->>DB: Check workspace permission
    DB->>PG: Read role and permissions
    PG-->>DB: Permission data
    DB-->>RBAC: Permission result

    alt Permission granted
        RBAC-->>GraphQL: Access granted
        GraphQL->>Service: create_tag()
        Service->>DB: Save tag
        DB->>PG: INSERT tag
        PG-->>DB: Saved tag
        DB-->>Service: Tag record
        Service-->>GraphQL: Created tag
        GraphQL-->>Postman: GraphQL response
        Postman-->>User: Tag created
    else Permission denied
        RBAC-->>GraphQL: Access denied
        GraphQL-->>Postman: Authorization error
    end
```

## 7.2 Assign tag to task

``` mermaid
sequenceDiagram
    autonumber
    actor User
    participant Postman
    participant GraphQL as Strawberry GraphQL
    participant JWT as JWT Validation
    participant RBAC as Permission Check
    participant Service as Tag Service
    participant DB as Database

    User->>Postman: Send assignTag mutation
    Postman->>GraphQL: Send request with access token
    GraphQL->>JWT: Validate access token
    JWT-->>GraphQL: Authenticated user
    GraphQL->>RBAC: Check required permission
    RBAC-->>GraphQL: Permission result

    alt Permission granted
        GraphQL->>Service: assign_tag_to_task()
        Service->>DB: Validate task, tag and workspace

        alt Task or tag is invalid
            DB-->>Service: Validation failed
            Service-->>GraphQL: Return error
        else Task and tag are valid
            Service->>DB: Check task_tags association

            alt Already assigned
                DB-->>Service: Assignment exists
                Service-->>GraphQL: Return already assigned
            else Not assigned
                Service->>DB: Insert task_id and tag_id into task_tags
                Note over DB: Same tag_id can be linked to multiple task_id values
                DB-->>Service: Assignment saved
                Service-->>GraphQL: Return success
            end
        end

        GraphQL-->>Postman: GraphQL response
        Postman-->>User: Display result
    else Permission denied
        GraphQL-->>Postman: Authorization error
        Postman-->>User: Display error
    end
```

## 7.3 Remove tag from task

``` mermaid
sequenceDiagram
    autonumber
    actor User
    participant Postman
    participant GraphQL as Strawberry GraphQL
    participant JWT as JWT Validation
    participant RBAC as Permission Check
    participant Service as Tag Service
    participant DB as Database

    User->>Postman: Send removeTag mutation
    Postman->>GraphQL: Send request with access token
    GraphQL->>JWT: Validate access token
    JWT-->>GraphQL: Authenticated user
    GraphQL->>RBAC: Check required permission
    RBAC-->>GraphQL: Permission result

    alt Permission granted
        GraphQL->>Service: remove_tag_from_task()
        Service->>DB: Check task and tag association

        alt Task is deleted
            DB-->>Service: Task is inactive
            Service-->>GraphQL: Return error
        else Task is active
            alt Association does not exist
                DB-->>Service: Association not found
                Service-->>GraphQL: Return error
            else Association exists
                Service->>DB: Delete task_tags association
                Note over Service,DB: Keep the tag in the tags table
                DB-->>Service: Association removed
                Service-->>GraphQL: Return success
            end
        end

        GraphQL-->>Postman: GraphQL response
        Postman-->>User: Display result
    else Permission denied
        GraphQL-->>Postman: Authorization error
        Postman-->>User: Display error
    end
```

------------------------------------------------------------------------

# 8. Task activity history

The Activity module reads activity history. Other modules create
activity records when they perform actions such as task creation,
updates, status changes, priority changes, and assignment.

``` mermaid
sequenceDiagram
    autonumber
    actor User
    participant Postman
    participant FastAPI
    participant GraphQL as Strawberry GraphQL
    participant JWT as JWT Validation
    participant RBAC as Permission Check
    participant Service as Activity Service
    participant DB as SQLAlchemy
    participant PG as Supabase PostgreSQL

    User->>Postman: Request task activities
    Postman->>FastAPI: getTaskActivities query + access token
    FastAPI->>GraphQL: Forward request
    GraphQL->>JWT: Validate access token
    JWT-->>GraphQL: Authenticated user identity
    GraphQL->>RBAC: Check VIEW_TASK permission
    RBAC->>DB: Check workspace permission
    DB->>PG: Read membership and permissions
    PG-->>DB: Permission data
    DB-->>RBAC: Permission result
    RBAC-->>GraphQL: Access granted
    GraphQL->>Service: get_task_activities(task_id)
    Service->>DB: Fetch task activity records
    DB->>PG: SELECT task_activity records
    PG-->>DB: Activity records
    DB-->>Service: Activity history
    Service-->>GraphQL: Return activities
    GraphQL-->>Postman: GraphQL response
    Postman-->>User: Display activity history
```

------------------------------------------------------------------------


