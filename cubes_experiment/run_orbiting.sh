start_time=$(date +%s)

animations=2
cubes=1
red=0

### Actual script vvvvvvvv
for i in $(seq 1 $animations); do
    blender --background --python red_blue_cubes_orbiting_around_z.py -- --number $cubes \
    --red $red --save "./animation_output/test_parallel/orbiting_${cubes}cubes_${red}red_$i" &
done

wait
### Actual script ^^^^^^^^


# Calculate the elapsed time in seconds
end_time=$(date +%s)
elapsed_time=$((end_time - start_time))
minutes=$(( (elapsed_time % 3600) / 60 ))
seconds=$((elapsed_time % 60))
echo "Total execution time: ${minutes}m ${seconds}s"

