#!/usr/bin/env groovy
import org.kohsuke.github.GHCommitState;
// Configuration variables //
properties([
    parameters([
        string(
            name: 'GIT_CRED',
            defaultValue: 'github',
            description: 'credentials id (ssh key for access to github)'
        ),
        string(
            name: 'GIT_REPO',
            defaultValue: 'mdanylyuk/python-poloniex',
            description: '[owner]/[repo]'
        ),
        string(
            name: 'IMAGE_NAME',
            defaultValue: 'mdanylyuk',
            description: 'docker build tag'
        )
    ])
    [
        $class: 'GithubProjectProperty', 
        displayName: 'Github project name', 
        projectUrlStr: ("https://github.com/${GIT_REPO}")],
    [
        $class: 'org.jenkinsci.plugins.workflow.job.properties.PipelineTriggersJobProperty',
        triggers: [[
            gitHubAuthId: 'github' 
            $class: 'org.jenkinsci.plugins.ghprb.GhprbTrigger',
            orgslist: "mdanylyuk",
            useGitHubHooks: true,
            permitAll: false,
            autoCloseFailedPullRequests: false,
            displayBuildErrorsOnDownstreamBuilds: true,
            triggerPhrase: ".*build-ci.*",
            skipPhrase: ".*skip-ci.*"
        ]]
    ]
])

//Build, testingm post-building proccess//
node('kubernetes'){
    stage('Checkout'){
        checkout([ $class: 'GitSCM',
            branches: [[name: "*/master"]],
            extensions: [[$class: 'WipeWorkspace']],
            userRemoteConfigs: [[
                credentialsId: GIT_CRED,
                url: "git@github.com:${GIT_REPO}.git"
            ]]
        ])
    }
    stage('Build'){
        def customImage = docker.build(
            "${IMAGE_NAME}:${env.BUILD_ID}",
            "--no-cache=true ."
        )
    }
    stage ('Post-build'){
        if (result.equals("SUCCESS")) {
            println "${env.BUILD_ID} is successed"
            def comment = pullRequest.comment("The build is succeeded")
        }
        else{
            println "${env.BUILD_ID} is failed or unstable"
            def comment = pullRequest.comment("The build is failed. Build log you can see here - ${env.BUILD_URL}/console") //Yuri asked about such link where he can see the result of failed build
        }
    }
}
