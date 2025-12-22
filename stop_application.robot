*** Settings ***
Library    Process
Library    OperatingSystem
Library    String

*** Variables ***
${PROJECT_DIR}=    ${CURDIR}
${DOCKER_COMPOSE_INFRA}=    ${PROJECT_DIR}/docker-compose.infra.yml
${DOCKER_COMPOSE_APP}=    ${PROJECT_DIR}/docker-compose.app.yml
${DB_CONTAINER}=    personal_finance_database

*** Keywords ***
Stop Docker Containers
    [Documentation]    Stop all Docker containers
    Log To Console    Stopping App containers...
    ${result_app}=    Run Process    docker-compose -f "${DOCKER_COMPOSE_APP}" down    shell=True
    Log To Console    App Stop Result: ${result_app.stdout}
    
    Log To Console    Stopping Infra containers...
    ${result_infra}=    Run Process    docker-compose -f "${DOCKER_COMPOSE_INFRA}" down    shell=True
    Log To Console    Infra Stop Result: ${result_infra.stdout}
    
    Run Keyword If    ${result_app.rc} != 0 or ${result_infra.rc} != 0    Fail    Failed to stop Docker containers
    Log To Console    All containers stopped successfully

Cleanup Dangling Docker Images
    [Documentation]    Remove dangling Docker images to free up space (keeps current images)
    Log To Console    \nCleaning up dangling Docker images...
    
    ${cmd_check}=    Set Variable    docker images -f "dangling=true" -q
    ${before}=    Run Process    ${cmd_check}    shell=True
    ${stdout}=    Set Variable    ${before.stdout.strip()}
    ${length}=    Get Length    ${stdout}
    
    Run Keyword If    ${length} == 0    Log To Console    No dangling images to clean up
    ...    ELSE    Remove Dangling Images

Remove Dangling Images
    [Documentation]    Remove dangling images and report results
    Log To Console    Removing dangling images...
    
    # Remove only dangling images (untagged and unused)
    ${cmd_prune}=    Set Variable    docker image prune -f
    ${result}=    Run Process    ${cmd_prune}    shell=True
    Log To Console    Cleanup result: ${result.stdout}
    
    # Report space reclaimed
    Run Keyword If    ${result.rc} == 0    Log To Console    Dangling images cleaned up successfully
    ...    ELSE    Log To Console    Warning: Some images could not be removed: ${result.stderr}


*** Tasks ***
Stop Personal Finance Application
    [Documentation]    Stop the Personal Finance Application and clean up dangling images
    Log To Console    \n=== Stopping Personal Finance Application ===\n
    Stop Docker Containers
    Cleanup Dangling Docker Images
    
    Log To Console    \n=== Application Stopped Successfully ===\n


