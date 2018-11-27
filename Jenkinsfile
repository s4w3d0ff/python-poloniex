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

    if (buildStatus == 'UNSTABLE') {
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
                    name: 'GIT_REPO_URIM',
                    defaultValue: 'mdanylyuk/python-1',
                    description: '[owner]/[repo]'
                ),
        string(
                    name: 'GIT_REPO_PATRICIA_COMMON',
                    defaultValue: 'mdanylyuk/python-patterns',
                    description: '[owner]/[repo]'
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
//                    onlyTriggerPhrase: true,
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
            branches: [[name: "origin/master"]],
            extensions: [[$class: 'WipeWorkspace']],
            userRemoteConfigs: [[
                credentialsId: "github",
                url: "git@github.com:${GIT_REPO}.git"
            ]]
        ])
        // Download patricia-common
            checkout([ 
                $class: 'GitSCM',
                branches: [[name: "*/master"]],
                extensions: [[$class: 'RelativeTargetDirectory', relativeTargetDir: 'patricia-common']],
                userRemoteConfigs: [[
                    credentialsId: "github",
                    url: "git@github.com:${GIT_REPO_PATRICIA_COMMON}.git"
                ]]
            ])
            // Download Urim
            checkout([ 
                $class: 'GitSCM',
                branches: [[name: "*/master"]],
                extensions: [[$class: 'RelativeTargetDirectory', relativeTargetDir: 'Urim']],
                userRemoteConfigs: [[
                    credentialsId: "github",
                    url: "git@github.com:${GIT_REPO_URIM}.git"
                ]]
            ])
    }
   stage ('Pre-Build') {
            sh '''
            echo "FROM ubuntu:xenial
            # Install base package dependencies
            RUN echo "deb http://archive.ubuntu.com/ubuntu cosmic main" >> /etc/apt/sources.list \\
            && apt-get update \\
            && apt-get install -y --no-install-recommends autoconf  automake  bzip2  build-essential  curl dpkg-dev  file  g++  gcc  git  imagemagick \\
            && apt-get install -y --no-install-recommends libbz2-dev libc6-dev libcurl4-openssl-dev libdb-dev libevent-dev libffi-dev libgdbm-dev \\
            && apt-get install -y --no-install-recommends libgeoip-dev libgeos-dev libglib2.0-dev libjpeg-dev libkrb5-dev liblzma-dev libmagickcore-dev \\
            && apt-get install -y --no-install-recommends libmagickwand-dev libncurses5-dev libncursesw5-dev libpng-dev libpq-dev libreadline-dev libsqlite3-dev \\
            && apt-get install -y --no-install-recommends libssl-dev libtool libwebp-dev libxml2-dev libxslt-dev libyaml-dev make patch ssh tk-dev vim xz-utils zlib1g-dev wget \\
            && rm -rf /var/lib/apt/lists/*

            #Install Python2,7, Python3.6, Pithon3.7, Pip2, Pip3.6, Pip3.7, Tox
            RUN apt update \\
            && apt install -y --no-install-recommends python python-dev python3 python3-wheel python3.6 python3.6-dev python3.7 python3.7-dev \\
            && curl https://bootstrap.pypa.io/get-pip.py -k -s | python \\
            && pip install tox \\
            && curl https://bootstrap.pypa.io/get-pip.py -k -s | python3.6 \\
            && curl https://bootstrap.pypa.io/get-pip.py -k -s | python3.7 \\
            && sed -i 's/python3.7/python2/' /usr/local/bin/pip \\
            && rm -rf /var/lib/apt/lists/*

            WORKDIR /root/urim

            COPY . ./

            CMD /bin/bash
            RUN rm -rf *@tmp \\
                && echo "git+file:///root/urim/patricia-common/@$(grep requirements.txt -e 'patricia-common' | cut -d ""@"" -f3)" >> requirements.txt \\
                && echo "git+file:///root/urim/Urim/@$(grep requirements.txt -e 'Urim' | cut -d ""@"" -f3)" >> requirements.txt \\
                && sed -i '/git+ssh:/d' requirements.txt \\
                tox" | tee Dockerfile
            '''
        }
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
