### Setting up scene information (settings for what the jobs should generate)

Run the file to make `scene_info.config` (from Git Bash for Windows),
because I want to have it locally / in Git history:

1. `cd "C:\Users\anaba\OneDrive\Desktop\Master Thesis\bias-action-recognition\daic\parallel_cube_render\scene_configuration"`
2. `sh generate_scene_info.sh`
3. IMPORTANT Make sure to update the amount of array jobs in `../render_cubes.sbatch` (`#SBATCH --array=1-90`) based on the amount of lines in the `../scene_info.config` file. 
4. Commit, push, and then pull on Cluster

