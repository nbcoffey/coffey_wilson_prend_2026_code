#!/bin/bash
#SBATCH --job-name=movie_pngs
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64GB
#SBATCH --partition=serc
#SBATCH --output=pngs_%j.out
#SBATCH --error=pngs_%j.err
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=nbcoffey@stanford.edu

# Load required modules (same as your OnDemand session)
module load system
module load viz
module load py-scipy/1.4.1_py36
module load py-matplotlib/3.2.1_py36
module load py-pandas/1.0.3_py36
module load py-sympy/1.1.1_py36

# Set display backend for matplotlib (important for headless execution)
export MPLBACKEND=Agg

# Print some info
echo "Job started at: $(date)"
echo "Running on node: $(hostname)"
echo "Job ID: $SLURM_JOB_ID"
echo "Working directory: $(pwd)"
echo "Available memory: $SLURM_MEM_PER_NODE MB"

# Run your script
python3 create_movie_pngs.py

echo "Job completed at: $(date)"
