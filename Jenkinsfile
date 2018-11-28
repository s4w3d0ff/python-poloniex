#!/usr/bin/env groovy
import hudson.model.*;
import org.kohsuke.github.GHCommitState;
// Configuration variables //

def notificationSlack (String buildStatus = 'STARTED') {
    // Build status of null means success.
    buildStatus = buildStatus ?: 'SUCCESS'

    def color
    def channel='jenkins'
    def message
    
    if (buildStatus == 'SUCCESS') {
        color = 'good'
        message = "*Urim:* Build: `${env.GIT_BRANCH}:${env.BUILD_NUMBER}` success. Logs: [<${env.RUN_CHANGES_DISPLAY_URL}|Changes>] [<${env.BUILD_URL}/console|Console>]"
    }

    else if (buildStatus == 'UNSTABLE') {
        color = 'warning'
        message = "*Urim:* Build: `${env.GIT_BRANCH}:${env.BUILD_NUMBER}` unstable. Logs: [<${env.RUN_CHANGES_DISPLAY_URL}|Changes>] [<${env.BUILD_URL}/console|Console>]"
    }
    else {
        color = 'danger'
        message = "*Urim:* Build: `${env.GIT_BRANCH}:${env.BUILD_NUMBER}` failed. Logs: [<${env.RUN_CHANGES_DISPLAY_URL}|Changes>] [<${env.BUILD_URL}/console|Console>]"
    }

    slackSend(color: color, channel:channel, message: message)
}

//Build, testing post-building proccess//
node ('master'){
    try {
        properties([
    parameters([
        string(
            name: 'GIT_CRED',
            defaultValue: 'github',
            description: 'credentials id (ssh key for access to github)',
            trim: true
        ),
        string(
            name: 'GIT_REPO',
            defaultValue: 'mdanylyuk/python-poloniex',
            description: '[owner]/[repo]',
            trim: true
        ),
        string(
            name: 'IMAGE_NAME',
            defaultValue: 'mdanylyuk',
            description: 'docker build tag',
            trim: true
        ),
        string(
            name: 'GITHUB_API',
            defaultValue: '18ec45fb-5283-4011-97da-a5e13eaf9dfd',
            description: 'GitHub API ID'
        )
    ]),
    [$class: 'GithubProjectProperty', 
        displayName: 'Github project name', 
        projectUrlStr: "https://github.com/mdanylyuk/python-poloniex"],
    [$class: 'org.jenkinsci.plugins.workflow.job.properties.PipelineTriggersJobProperty',
        triggers: [[
                    $class: 'org.jenkinsci.plugins.ghprb.GhprbTrigger',
                    gitHubAuthId: "18ec45fb-5283-4011-97da-a5e13eaf9dfd",
                    orgslist: "mdanylyuk",
                    cron: 'H/5 * * * *',
                    triggerPhrase: ".*build-ci.*",
                    skipPhrase: ".*skip-ci.*",
                    //uncomment next option if need to use trigger only with trigger phrase (now trigger run after creating PR, trigger phrase, commints)
                    onlyTriggerPhrase: true,
                    useGitHubHooks: true,
                    permitAll: true,
                    autoCloseFailedPullRequests: false,
                    displayBuildErrorsOnDownstreamBuilds: true,
                    extensions: [[
                        $class: 'org.jenkinsci.plugins.ghprb.extensions.status.GhprbSimpleStatus',
                        commitStatusContext: 'Docker Build (running tests)',
                        showMatrixStatus: false,
                        triggeredStatus: 'Starting job...',
                        startedStatus: 'Building...',
                        completedStatus: [
                            [
                                $class: 'org.jenkinsci.plugins.ghprb.extensions.comments.GhprbBuildResultMessage',
                                message: 'Success',
                                result: GHCommitState.SUCCESS
                            ],
                            [
                                $class: 'org.jenkinsci.plugins.ghprb.extensions.comments.GhprbBuildResultMessage',
                                message: 'Failed',
                                result: GHCommitState.FAILURE
                            ]
                        ]
                    ]]
                ]]
    ]
])
     stage ('Checkout') {
        slackSend([
            color:'good', 
            channel:'jenkins', 
            message:"*Urim:* Build: `${env.GIT_BRANCH}:${env.BUILD_NUMBER}` Running..."
        ])
        //println "ghprbSourceBranch: ${ghprbSourceBranch} || ghprbTargetBranch: ${ghprbTargetBranch} || ghprbPullId: ${ghprbPullId}"
        checkout([
            $class: 'GitSCM',
            doGenerateSubmoduleConfigurations: false,
            submoduleCfg: [],
            branches: [[name: "*/${env.GIT_BRANCH}"]],
            extensions: [[$class: 'WipeWorkspace']],
            userRemoteConfigs: [[
                credentialsId: "github",
                url: "git@github.com:mdanylyuk/python-poloniex.git"
            ]]
        ])
   }
   /*stage ('Pre-Build') {
            sh '''
            echo "" | tee Dockerfile
            '''
        }*/
    stage ('Build') {
        slackSend ([
            color:'good', 
            channel:'jenkins', 
            message:"*Urim:* Build: `${env.GIT_BRANCH}:${env.BUILD_NUMBER}` Testing..."
        ])
        docker.build(
            "${IMAGE_NAME}:${env.BUILD_ID}",
            "--no-cache=true ."
        )
    }
    }
    catch (Exception ex) {
        println "Catching exception"
        currentBuild.result = 'FAILED'
        echo ex.toString()

        // Throw RejectedAccessException again if its a script privilege error
        if (ex.toString().contains('RejectedAccessException')) {
            throw ex
        }
    }
    finally {
        notificationSlack(currentBuild.result)
    }
}
