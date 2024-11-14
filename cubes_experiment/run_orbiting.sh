start_time=$(date +%s)

### Actual script vvvvvvvv
for i in {1..5}; do
    echo "Running #$i"
    blender --background --python red_blue_cubes_orbiting_around_z.py -- --save "./animation_output/test_parallel/orbiting$i" &
done

wait
### Actual script ^^^^^^^^


# Calculate the elapsed time in seconds
end_time=$(date +%s)
elapsed_time=$((end_time - start_time))
minutes=$(( (elapsed_time % 3600) / 60 ))
seconds=$((elapsed_time % 60))
echo "Total execution time: ${minutes}m ${seconds}s"

