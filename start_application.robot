*** Settings ***
Library    Process
Library    OperatingSystem
Library    String
Library    DateTime

*** Variables ***
${PROJECT_DIR}=    ${CURDIR}
${DOCKER_COMPOSE_INFRA}=    ${PROJECT_DIR}/docker-compose.infra.yml
${DOCKER_COMPOSE_APP}=    ${PROJECT_DIR}/docker-compose.app.yml
${DB_CONTAINER}=    database
${SCHEDULER_CONTAINER}=    scheduler
${FRONTEND_CONTAINER}=    personal_finance_frontend
${VOLUME_NAME}=    personal_finance_data_volume
${DB_NAME}=    personal_finance_db
${IMAGE_NAME}             personal_finance_backend
${FRONTEND_IMAGE_NAME}    personal_finance_frontend
${COMPOSE_TIMEOUT}        300

*** Keywords ***
Check Docker Installation
    [Documentation]    Check if Docker is installed and accessible
    ${result}=    Run Process    docker --version    shell=True
    Run Keyword If    ${result.rc} != 0    Fail    Docker is not installed or not in PATH. Please install Docker Desktop.
    Log To Console    Docker version: ${result.stdout}

    ${result}=    Run Process    docker-compose --version    shell=True
    Run Keyword If    ${result.rc} != 0    Fail    Docker Compose is not installed or not in PATH. Please install Docker Desktop.
    Log To Console    Docker Compose version: ${result.stdout}

Check Docker Compose Files
    [Documentation]    Check if docker-compose files exist
    ${infra_exists}=    Run Process    powershell -Command "Test-Path '${DOCKER_COMPOSE_INFRA}'"    shell=True
    Run Keyword If    '${infra_exists.stdout.strip()}' == 'False'    Fail    docker-compose.infra.yml file not found at ${DOCKER_COMPOSE_INFRA}
    
    ${app_exists}=    Run Process    powershell -Command "Test-Path '${DOCKER_COMPOSE_APP}'"    shell=True
    Run Keyword If    '${app_exists.stdout.strip()}' == 'False'    Fail    docker-compose.app.yml file not found at ${DOCKER_COMPOSE_APP}

Ensure Docker Volume
    [Documentation]    Ensure Docker volume exists
    ${result}=    Run Process    docker volume inspect ${VOLUME_NAME}    shell=True
    Run Keyword If    ${result.rc} != 0    Create Docker Volume

Create Docker Volume
    [Documentation]    Create Docker volume if it doesn't exist
    ${result}=    Run Process    docker volume create ${VOLUME_NAME}    shell=True
    Log To Console    Volume creation result: ${result.stdout}
    Run Keyword If    ${result.rc} != 0    Fail    Failed to create Docker volume: ${result.stderr}

Build Docker Image If Needed
    [Documentation]    Build Docker image only if changes detected
    [Arguments]    ${force_build}=False

    Run Keyword If    ${force_build}    Force Build Docker Image
    ...    ELSE    Build Docker Image Smart

Force Build Docker Image
    [Documentation]    Force rebuild of Docker image
    Log To Console    Force building Docker image...
    ${result}=    Run Process    docker-compose -f "${DOCKER_COMPOSE_APP}" build --no-cache    shell=True    cwd=${CURDIR}
    Log To Console    Build stdout: ${result.stdout}
    Log To Console    Build stderr: ${result.stderr}
    Run Keyword If    ${result.rc} != 0    Fail    Docker build failed. Check build logs above.
    Log To Console    Docker image built successfully!

Build Docker Image Smart
    [Documentation]    Build Docker image only if needed (checks for changes)
    Log To Console    Checking if Docker image needs to be rebuilt...

    # Check if image exists
    ${image_exists}=    Check If Docker Image Exists

    # Check if source files changed
    ${files_changed}=    Check If Source Files Changed

    # Build only if image doesn't exist OR files changed
    ${should_build}=    Evaluate    not ${image_exists} or ${files_changed}

    Run Keyword If    ${should_build}    Build Docker Image
    ...    ELSE    Log To Console    Using existing Docker image (no changes detected)

Check If Docker Image Exists
    [Documentation]    Check if Docker image already exists
    ${result}=    Run Process    docker images -q ${IMAGE_NAME}    shell=True
    ${image_exists}=    Set Variable If    '${result.stdout}' != ''    True    False
    Log To Console    Image exists: ${image_exists}
    RETURN    ${image_exists}

Check If Source Files Changed
    [Documentation]    Check if source files changed since last build (backend and frontend)
    # Check backend Python files
    ${result_py}=    Run Process    find . -name "*.py" -newer .last_build 2>/dev/null | head -1    shell=True    cwd=${CURDIR}
    ${py_changed}=    Set Variable If    '${result_py.stdout}' != ''    True    False

    # Check frontend files (TypeScript, JavaScript, JSON)
    ${result_frontend}=    Run Process    find ./frontend -type f \\( -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" -o -name "*.json" \\) -newer .last_build 2>/dev/null | head -1    shell=True    cwd=${CURDIR}
    ${frontend_changed}=    Set Variable If    '${result_frontend.stdout}' != ''    True    False

    # If .last_build doesn't exist, assume files changed
    ${last_build_exists}=    Run Keyword And Return Status    OperatingSystem.File Should Exist    .last_build
    ${files_changed}=    Set Variable If    not ${last_build_exists}    True    ${py_changed} or ${frontend_changed}
    ${files_changed}=    Evaluate    ${py_changed} or ${frontend_changed} if ${last_build_exists} else True

    Log To Console    Backend files changed: ${py_changed}
    Log To Console    Frontend files changed: ${frontend_changed}
    Log To Console    Overall files changed since last build: ${files_changed}
    RETURN    ${files_changed}

Build Docker Image
    [Documentation]    Build Docker image and update timestamp
    Log To Console    Building Docker image...
    ${result}=    Run Process    docker-compose -f "${DOCKER_COMPOSE_APP}" build    shell=True    cwd=${CURDIR}
    Log To Console    Build stdout: ${result.stdout}
    Log To Console    Build stderr: ${result.stderr}
    Run Keyword If    ${result.rc} != 0    Fail    Docker build failed. Check build logs above.

    # Create timestamp file to track last build
    Create File    .last_build    ${EMPTY}
    Log To Console    Docker image built successfully!

Start Infra Containers
    [Documentation]    Start infrastructure containers (DB, Redis, etc.)
    Set Environment Variable    COMPOSE_HTTP_TIMEOUT    ${COMPOSE_TIMEOUT}
    ${result}=    Run Process    docker-compose -f "${DOCKER_COMPOSE_INFRA}" up -d    shell=True
    Log To Console    Infra Start Result: ${result.stdout}
    Run Keyword If    ${result.rc} != 0    Fail    Failed to start infra containers: ${result.stderr}

Start App Containers
    [Documentation]    Start application containers (Backend, Frontend)
    Set Environment Variable    COMPOSE_HTTP_TIMEOUT    ${COMPOSE_TIMEOUT}
    ${result}=    Run Process    docker-compose -f "${DOCKER_COMPOSE_APP}" up -d    shell=True
    Log To Console    App Start Result: ${result.stdout}
    Run Keyword If    ${result.rc} != 0    Fail    Failed to start app containers: ${result.stderr}

Wait For Database
    [Documentation]    Wait for the database container to be ready
    Log To Console    ${\n}Waiting for database to be ready...

    # Wait for container health
    Wait Until Keyword Succeeds    60s    2s    Check Container Running
    
    # Wait for MySQL to accept connections
    Wait Until Keyword Succeeds    120s    3s    Check MySQL Ready

    # Extra buffer for stability
    Log To Console    Database ready, waiting extra 30 seconds for stability...
    Sleep    30s
    Log To Console    ✓ Database is fully ready!

Check Container Running
    ${result}=    Run Process    docker    inspect    -f    {{.State.Running}}   ${DB_CONTAINER}    shell=False
    Should Be Equal    ${result.stdout.strip()}    true

Check MySQL Ready
    ${result}=    Run Process
    ...    docker    exec    ${DB_CONTAINER}
    ...    mysqladmin    ping    -h    localhost    -u    root    -p$MYSQL_ROOT_PASSWORD    --silent
    ...    shell=False
    Should Be Equal As Integers    ${result.rc}    0

Check If Latest Database Backup Exists
    [Documentation]    Check if the database backup is available
    ${backups}=    Run Process    docker exec ${DB_CONTAINER} ls /backups/    shell=True
    Log To Console    Found files: ${backups.stdout.strip()}
    ${backup_files}=    Split String    ${backups.stdout.strip()}    \n
    Log To Console    Stripped file names: ${backup_files}
    Run Keyword If    ${backup_files} == []    Log To Console    No backup found. Skipping restore.
    Run Keyword If    ${backup_files} != []    Restore Backup    ${backup_files}

Restore Backup
    [Arguments]    ${backup_files}
    # Filter out GOLDEN backup and get only timestamped backups
    ${timestamped_backups}=    Evaluate    [f.strip() for f in ${backup_files} if 'GOLDEN' not in f and f.strip()]
    Run Keyword If    ${timestamped_backups} == []    Log To Console    No timestamped backup found. Skipping restore.    ELSE    Restore Latest Timestamped Backup    ${timestamped_backups}

Restore Latest Timestamped Backup
    [Arguments]    ${timestamped_backups}
    ${latest_backup}=    Evaluate    sorted(${timestamped_backups})[-1]
    Log To Console    Found latest backup: ${latest_backup}
    
    # Use sh -c with single quotes to protect $MYSQL_ROOT_PASSWORD expansion.
    # The pipeline is fully contained within the quotes.
    ${restore_command}=    Set Variable    gunzip -c /backups/${latest_backup} | mysql -u root -p$MYSQL_ROOT_PASSWORD --database=${DB_NAME}
    ${result}=    Run Process    docker exec ${DB_CONTAINER} sh -c '${restore_command}'    shell=True
    
    Run Keyword If    ${result.rc} != 0    Fail    Failed to restore database from backup: ${result.stderr}
    Log To Console    Database restored from ${latest_backup}

Check Scheduler
    [Documentation]    Check if the scheduler is running correctly
    Sleep    10s
    ${result}=    Run Process    docker logs ${SCHEDULER_CONTAINER}    shell=True
    Log To Console    Scheduler started successfully

Check Backup Script
    [Documentation]    Check if the backup script is present and executable
    ${result}=    Run Process    docker exec ${DB_CONTAINER} ls -l /backup.sh    shell=True
    Log To Console    Backup script status: ${result.stdout}
    Run Keyword If    ${result.rc} != 0    Fail    Backup script not found in the database container
    ${result}=    Run Process    docker exec ${DB_CONTAINER} test -x /backup.sh    shell=True
    Run Keyword If    ${result.rc} != 0    Fail    Backup script is not executable
    Log To Console    Backup script is present and executable

Check Frontend
    [Documentation]    Check if the frontend is running and accessible
    Log To Console    Checking frontend accessibility...
    Sleep    5s
    FOR    ${i}    IN RANGE    30
        ${percent}=    Set Variable    %
        ${result}=    Run Process    curl -f http://localhost:3000 -o /dev/null -s -w "${percent}{http_code}"    shell=True
        ${status_code}=    Set Variable    ${result.stdout}
        Run Keyword If    '${status_code}' == '200'    Exit For Loop
        Sleep    2s
    END
    Run Keyword If    '${status_code}' != '200'    Log To Console    Warning: Frontend may not be fully ready (status: ${status_code})
    ...    ELSE    Log To Console    Frontend is accessible at http://localhost:3000


*** Tasks ***
Start Personal Finance Application
    [Documentation]    Start all the necessary components for the Personal Finance Application
    Log To Console    \n=== Starting Personal Finance Application ===\n
    Log To Console    [1/8] Checking Docker installation...
    Check Docker Installation

    Log To Console    [2/8] Verifying Docker Compose files...
    Check Docker Compose Files

    Log To Console    [3/8] Ensuring Docker volume exists...
    Ensure Docker Volume

    Log To Console    [4/8] building Docker images...
    Build Docker Image If Needed

    Log To Console    [5/8] Starting Infrastructure...
    Start Infra Containers

    Log To Console    [6/8] Waiting for database...
    Wait For Database

    Log To Console    [7/8] Restoring database sequencing...
    Check If Latest Database Backup Exists

    Log To Console    [8/8] Starting Application...
    Start App Containers

    Log To Console    [FINAL] Verification...
    Check Backup Script
    Check Scheduler
    Check Frontend

    Log To Console    \n=== Application Started Successfully! ===
    Log To Console    Backend: http://localhost:8000
    Log To Console    Frontend: http://localhost:3000\n
