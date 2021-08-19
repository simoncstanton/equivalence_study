#!/bin/bash
#PBS -N exp_selfplay_parameter_study_job
#PBS -l ncpus=1
#PBS -l mem=200mb
#PBS -l walltime=03:00:00
#PBS -m ea
#PBS -WMail_Users=__USER_EMAIL__
#PBS -o /scratch/__USER__/obs_exp/pbs_output/
#PBS -e /scratch/__USER__/obs_exp/pbs_output/
#PBS -J 0-99:1

trap "echo "---------------------"$'\r'; qstat -f $PBS_JOBID" EXIT


IFS='[' read -ra JOBID_ARRAY <<< $PBS_JOBID
PARENT_JOBID=${JOBID_ARRAY[0]}
REMAINDER_JOBID_ARRAY=${JOBID_ARRAY[1]}

IFS=']' read -ra SUB_JOBID_ARRAY <<< $REMAINDER_JOBID_ARRAY
SUB_JOBID=${SUB_JOBID_ARRAY[0]}

JOBID=${PARENT_JOBID}_${SUB_JOBID}
JOB_DIR=$JOBID

RESULTS_DIR=~/kunanyi/results/experiments/selfplay_parameter_study/$PARENT_JOBID/$JOB_DIR
echo "SHELL:: Creating RESULTS_DIR: " $RESULTS_DIR
mkdir -p $RESULTS_DIR


SCRATCH_DIR=/scratch/$USER
SCRATCH_JOB_DIR=$SCRATCH_DIR/$JOBID
echo "SHELL:: Creating SCRATCH_JOB_DIR: " $SCRATCH_JOB_DIR
mkdir $SCRATCH_JOB_DIR


# create journal job dir in USER HOME
JOURNAL_DEST=~/kunanyi/results/obs_exp/journal/$PARENT_JOBID/sj_summary
mkdir -p $JOURNAL_DEST

# create (if not exist) obs_exp/heartbeat and obs_exp/journal on SCRATCH
SCRATCH_OBS_EXP_HEARTBEAT=$SCRATCH_DIR/obs_exp/heartbeat
mkdir -p $SCRATCH_OBS_EXP_HEARTBEAT

SCRATCH_OBS_EXP_JOURNAL=$SCRATCH_DIR/obs_exp/journal
mkdir -p $SCRATCH_OBS_EXP_JOURNAL


LINE_INDEX=$((PBS_ARRAY_INDEX + 1))
PARAMETERS=`sed -n "${LINE_INDEX} p" "${PBS_O_WORKDIR}/pbs_scripts/parameter_input_files/parameter_input_2_dimensions-from_point_one-100lines.txt"`
parameterArray=($PARAMETERS)
i=${parameterArray[0]}
j=${parameterArray[1]}
AGENT_PARAMETERS="alpha=$i:gamma=$j"
echo "SHELL:: AGENT_PARAMETERS: " $AGENT_PARAMETERS

module load EasyBuild/4.2.2
module load Python/3.7.4-GCCcore-8.3.0

cd ~/virtualenvs/agent_model/bin
source activate

cd ${PBS_O_WORKDIR}

python3 -m run_exp.exp_selfplay_parameter_study -j $PBS_JOBID -w $SCRATCH_DIR -g g111 -r ordinal_norm.3 -s actor_critic_1ed_replacetrace -e 500 -t 1000 -p "$AGENT_PARAMETERS" -k false -z true -c true -l false

cd $SCRATCH_DIR || exit 1

ARCHIVE_FILENAME=$JOBID.tar.gz
echo "SHELL:: creating archive: " $ARCHIVE_FILENAME
tar --remove-files --create --gzip --file=$ARCHIVE_FILENAME -C $SCRATCH_DIR $JOB_DIR

echo "SHELL:: moving archive ..."
mv -fv $ARCHIVE_FILENAME $RESULTS_DIR


# remove heartbeat and journal files
HEARTBEAT_FILE=exp_$JOBID.heartbeat
JOURNAL_FILE=exp_${JOBID}_summary.json

echo "SHELL:: deleting heartbeat file from SCRATCH: " $HEARTBEAT_FILE
rm -f $SCRATCH_OBS_EXP_HEARTBEAT/$HEARTBEAT_FILE

echo "SHELL:: moving journal file from SCRATCH to USER HOME: " $JOURNAL_FILE $JOURNAL_DEST
mv -fv $SCRATCH_OBS_EXP_JOURNAL/$JOURNAL_FILE $JOURNAL_DEST



echo "SHELL:: Finished."
