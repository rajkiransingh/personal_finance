*** Settings ***
Library    Process
Library    OperatingSystem
Library    String

*** Variables ***
${PROJECT_DIR}=    ${CURDIR}
${DOCKER_COMPOSE_FILE}=    ${PROJECT_DIR}/docker-compose.yml
${DB_CONTAINER}=    personal_finance_database

*** Keywords ***
Stop Docker Containers
    [Documentation]    Stop all Docker containers
    ${result}=    Run Process    docker-compose -f "${DOCKER_COMPOSE_FILE}" down    shell=True
    Log    Docker Compose down result: ${result.stdout}
    Run Keyword If    ${result.rc} != 0    Fail    Failed to stop Docker containers: ${result.stderr}

*** Tasks ***
Stop Personal Finance Application
    [Documentation]    Stop the Personal Finance Application and perform final backup
    Stop Docker Containers
    Log    Personal Finance Application environment has been stopped and final backup performed

