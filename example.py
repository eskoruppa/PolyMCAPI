from polymcapi import PolyMC

run_dir = "example/"
num_bp = 101
steps = 400000
xyzn  = 1000


sim = PolyMC(f"./{run_dir}/PolyMC")
print(f"Using PolyMC v{sim.version}")

# First run
result = sim.run(
    input_file=f"{run_dir}/input",
    output_dir=f"{run_dir}/output/run_001",
    params={"num_bp": num_bp, 'idb' : f'{run_dir}/TWLC.idb',  "seq" : f"{run_dir}/seq", 'steps': steps, 'equi': 0, 'XYZn': xyzn},
    capture_output=True,
)

print('')
print("#" * 80)
print("#" * 80)
  
print(result["stdout"])
if result["stderr"] != '':
    print("STDERR:")
    print(result["stderr"])  

for key in result.keys():
    if key not in ["stdout", "stderr"]:
        print(f"{key} = {result[key]}")
