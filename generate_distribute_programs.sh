python3 ./src/generate_distribute_programs.py \
--topology-path "/home/p4/new-switch-de-composer/topology-json/topology_e1_with_policies.json" \
--dependencies-folder-path "/home/p4/new-switch-de-composer/dependencies-json" \
--policies-folder-path "/home/p4/new-switch-de-composer/policies" \
--output-folder "/home/p4/new-switch-de-composer/outputs" \
--mininet True \
--auto-run True 

#python3 ./src/generate_distribute_programs.py "$@"