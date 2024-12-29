*** Settings ***
Library    Process
Library    OperatingSystem
Library    String
Library    DateTime

*** Variables ***
${PROJECT_DIR}=    ${CURDIR}
${DOCKER_COMPOSE_FILE}=    ${PROJECT_DIR}\\docker-compose.yml
${DB_CONTAINER}=    database
${SCHEDULER_CONTAINER}=    scheduler
${VOLUME_NAME}=    personal_finance_data_volume

*** Keywords ***
Check Docker Installation
    [Documentation]    Check if Docker is installed and accessible
    ${result}=    Run Process    docker --version    shell=True
    Run Keyword If    ${result.rc} != 0    Fail    Docker is not installed or not in PATH. Please install Docker Desktop.
    Log    Docker version: ${result.stdout}

    ${result}=    Run Process    docker-compose --version    shell=True
    Run Keyword If    ${result.rc} != 0    Fail    Docker Compose is not installed or not in PATH. Please install Docker Desktop.
    Log    Docker Compose version: ${result.stdout}

Check Docker Compose File
    [Documentation]    Check if docker-compose.yml file exists
    ${file_exists}=    Run Process    powershell -Command "Test-Path '${DOCKER_COMPOSE_FILE}'"    shell=True
    Run Keyword If    '${file_exists.stdout.strip()}' == 'False'    Fail    docker-compose.yml file not found at ${DOCKER_COMPOSE_FILE}

Ensure Docker Volume
    [Documentation]    Ensure Docker volume exists
    ${result}=    Run Process    docker volume inspect ${VOLUME_NAME}    shell=True
    Run Keyword If    ${result.rc} != 0    Create Docker Volume

Create Docker Volume
    [Documentation]    Create Docker volume if it doesn't exist
    ${result}=    Run Process    docker volume create ${VOLUME_NAME}    shell=True
    Log    Volume creation result: ${result.stdout}
    Run Keyword If    ${result.rc} != 0    Fail    Failed to create Docker volume: ${result.stderr}

Start Docker Containers
    [Documentation]    Start all the necessary Docker containers
    ${result}=    Run Process    docker-compose -f "${DOCKER_COMPOSE_FILE}" up -d    shell=True
    Log    Docker Compose up result: ${result.stdout}
    Run Keyword If    ${result.rc} != 0    Fail    Failed to start Docker containers: ${result.stderr}

Wait For Database
    [Documentation]    Wait for the database container to be ready
    FOR    ${i}    IN RANGE    30
        ${result}=    Run Process    docker exec ${DB_CONTAINER} mysqladmin ping -h localhost -u root -ppassword    shell=True
        Run Keyword If    ${result.rc} == 0    Exit For Loop
        Sleep    1s
    END
    Run Keyword If    ${result.rc} != 0    Fail    Database container did not become ready in time

Check Scheduler
    [Documentation]    Check if the scheduler is running correctly
    Sleep    10s    # Give the scheduler more time to initialize
    ${result}=    Run Process    docker logs ${SCHEDULER_CONTAINER}    shell=True
    Log    Scheduler logs: ${result.stdout}
    Log    Scheduler started successfully

Check Backup Script
    [Documentation]    Check if the backup script is present and executable
    ${result}=    Run Process    docker exec ${DB_CONTAINER} ls -l /backup.sh    shell=True
    Log    Backup script status: ${result.stdout}
    Run Keyword If    ${result.rc} != 0    Fail    Backup script not found in the database container
    ${result}=    Run Process    docker exec ${DB_CONTAINER} test -x /backup.sh    shell=True
    Run Keyword If    ${result.rc} != 0    Fail    Backup script is not executable
    Log    Backup script is present and executable

*** Tasks ***
Start Personal Finance Application
    [Documentation]    Start all the necessary components for the Personal Finance Application
    Check Docker Installation
    Log To Console    Docker installation checked
    Check Docker Compose File
    Log To Console    Docker compose file checked
    Ensure Docker Volume
    Log To Console    Docker volume checked
    Start Docker Containers
    Log To Console    Docker container started
    Wait For Database
    Log To Console    Database started and wait is over
    Check Backup Script
    Log To Console    Backup script is checked
    Check Scheduler
    Log To Console    Personal Finance Application environment is ready

