## Tutorial for DAIC

### Initial setup
1. Inside WSL a file `.ssh/config` like [config](config).
2. Run `ssh daic` and put password twice.
3. `pwd` to see you are in your `/home/nfs/abaltaretu` folder
4. `cd /tudelft.net/staff-umbrella/StudentsCVlab/` to see that you have access to the data folder
5. `mkdir abaltaretu` make my dir
6. `mkdir -p /tudelft.net/staff-umbrella/StudentsCVlab/abaltaretu/.conda` make a .conda directory in staff-bulk
7. `ln -s /tudelft.net/staff-umbrella/StudentsCVlab/abaltaretu/.conda $HOME/.conda` create a symbolic link to .conda from my home directory
8. `conda init`
9. Conda env for pytorch and cuda: make a file and put file contents from [here](https://gitlab.tudelft.nl/pattern-recognition-and-bioinformatics/wiki/-/snippets/265/raw/main/pytorch.yml) 
10. `conda env create -f pytorch.yml`

Blender:
11. Check blender module exists: `module avail blender`, and see more detailed info about it `module spider blender`.
12. Download a "Release" ready version: `wget https://cdn.builder.blender.org/download/daily/archive/blender-4.2.4-candidate+v42.9e33bed52cc4-linux.x86_64-release.tar.xz`
13. Extract the file `tar -xf blender-4.2.4-candidate+v42.9e33bed52cc4-linux.x86_64-release.tar.xz`

## Run every time
1. Run `ssh daic` and put password twice.
2. Conda
   1. ````
      module use /opt/insy/modulefiles
      module load miniconda/3.10
      ````
   2. `conda init`
   3. ```
      if [ -f ~/.bashrc ]; then
      . ~/.bashrc
      fi
      ```
3. `cd /tudelft.net/staff-umbrella/StudentsCVlab/abaltaretu`

See: https://gitlab.tudelft.nl/pattern-recognition-and-bioinformatics/wiki/-/wikis/HPC-quickstart-guide


## Clone Git repo
`git clone https://github.com/ana-baltaretu/bias-action-recognition.git`
`git pull`

## Copying files
`scp daic:/<remote_path_to_file> /<local_path>`
`scp daic:/tudelft.net/staff-umbrella/StudentsCVlab/abaltaretu/test_orbiting_green/blender_error_11298693.log /mnt/c/Users/anaba/OneDrive/Desktop/cluster/`

## Running/Checking jobs
```sbatch <job_file>.sbatch```
```slurmtop```

Retrieve information about scheduled and running jobs:
```scontrol show job <job_id>``` 

See info about jobs located in the Slurm scheduling queue.
`squeue -u $abaltaretu` or `squeue --me`

Check detailed Job history:
```sacct --format=JobID,JobName,State,Elapsed,MaxRSS,Start,End -j <jobid>```


## Containerization - AppTainer
Pull image:
``apptainer pull docker://ubuntu:20.04``

Enter shell and run commands:
```
apptainer shell ubuntu_20.04.sif
echo "Hello from Apptainer!"
exit
```

Execute command:
``apptainer exec ubuntu_20.04.sif echo "Hello from apptainer! "``

Run the container:
``apptainer run ubuntu_20.04.sif``

Cache cleanup
``apptainer cache clean -f``

Apptainer home env variable:
``APPTAINER_HOME="/usr/bin/apptainer"``

### Binding / data transfer
Binding folders also saves files after execution
Good practice to bind from the command line (not image file) for more flexibility:
``$ apptainer exec -B /opt -B /data:/mnt image.sif``

Using NVIDIA GPU: ``apptainer exec --nv image.sif python my_script.py``


# 
cd /tudelft.net/staff-umbrella/StudentsCVlab/abaltaretu


## Resources
- [Slurm cheatsheet](https://slurm.schedmd.com/pdfs/summary.pdf)
- [Apptainer template](https://gitlab.ewi.tudelft.nl/reit/apptainer-template)
- [Hands-on access DAIC 101](https://reit.pages.ewi.tudelft.nl/course-daic-101/023-handson-daic-access.html)
- [Hands-on SLURM](https://reit.pages.ewi.tudelft.nl/course-daic-101/032-handson-slurm.html)
- [Best practices Disk IO](https://reit.pages.ewi.tudelft.nl/course-daic-101/047-best-practices.html#/best-practices-for-disk-io)
