#!/bin/bash
#PBS -N exp_selfplay_parameter_study_job
#PBS -l ncpus=1
#PBS -l mem=2gb
#PBS -l walltime=01:00:00
#PBS -m ea
#PBS -WMail_Users=__USER_EMAIL__
#PBS -o /u/__USER__/kunanyi/results/obs_exp/pbs_output/
#PBS -e /u/__USER__/kunanyi/results/obs_exp/pbs_output/

trap "echo "---------------------"$'\r'; qstat -f $PBS_JOBID" EXIT


IFS='.' read -ra JOBID_ARRAY <<< $PBS_JOBID
PARENT_JOBID=${JOBID_ARRAY[0]}

JOBID=${PARENT_JOBID}_0
JOB_DIR=$JOBID

RESULTS_DIR=~/kunanyi/results/experiments/selfplay_parameter_study/$PARENT_JOBID/$JOB_DIR
echo "SHELL:: Creating RESULTS_DIR: " $RESULTS_DIR
mkdir -p $RESULTS_DIR


SCRATCH_DIR=/scratch/$USER
SCRATCH_JOB_DIR=$SCRATCH_DIR/$JOBID
echo "SHELL:: Creating SCRATCH_JOB_DIR: " $SCRATCH_JOB_DIR
mkdir $SCRATCH_JOB_DIR


AGENT_PARAMETERS="alpha=0.2:gamma=0.3"
echo "SHELL:: AGENT_PARAMETERS: " $AGENT_PARAMETERS

module load EasyBuild/4.2.2
module load Python/3.7.4-GCCcore-8.3.0

cd ~/virtualenvs/agent_model/bin
source activate

cd ${PBS_O_WORKDIR}

python3 -m run_exp.exp_selfplay_parameter_study -j $PBS_JOBID -w $SCRATCH_DIR -g pd -r scalar -s actor_critic_1ed -e 50 -t 1000 -p "$AGENT_PARAMETERS"

cd $SCRATCH_DIR || exit 1

ARCHIVE_FILENAME=$JOBID.tar.gz
echo "SHELL:: creating archive: " $ARCHIVE_FILENAME
tar --remove-files --create --gzip --file=$ARCHIVE_FILENAME -C $SCRATCH_DIR $JOB_DIR

echo "SHELL:: moving archive ..."
mv -fv $ARCHIVE_FILENAME $RESULTS_DIR

echo "SHELL:: Finished."
