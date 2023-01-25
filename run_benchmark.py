import json
import sys
import os
import re
import time
from multiprocessing import Process
from shlex import quote
from typing import Dict


class BenchmarkDefinition:
	def __init__(self, model_name: str, model_file: str, size: int, phenotype_name:str, phenotype: Dict):
		self.model_name = model_name
		self.model_file = model_file
		self.size = size
		self.phenotype_name = phenotype_name
		self.phenotype = phenotype

RE_TIME = re.compile("\\s*real\\s*(\\d+\\.?\\d*)\\s*")

# Spawn a new process external process.
def SPAWN(command):
	print("Spawn:", command)
	result = os.system(command)
	sys.exit(result)

if __name__ == "__main__":
	# Set timeout binary based on OS (macOS needs gtimeout)
	TIMEOUT = 'none'
	PARALLEL = 8
	CUT_OFF = '4h'
	SCRIPT = 'python3 main.py'
	BENCH_DIR = "phentoype_benchmark"
	AGGREGATION_LIST = []

	OUT_DIR = BENCH_DIR.replace("/", "_") + "_" + os.path.basename(SCRIPT)
	if PARALLEL > 0:
		OUT_DIR = OUT_DIR + "_parallel"
	OUT_DIR = "_run_" + OUT_DIR + "_" + str(int(time.time()))
	os.mkdir(OUT_DIR)

	TIMES = open(OUT_DIR + "/" + BENCH_DIR.replace("/", "_") + "_" + os.path.basename(SCRIPT) + "_times.csv", "w")
	def PROCESS_RESULT(process, name, phenotype, output_file):
		print("Finished:", output_file)
		is_success = process.exitcode == 0
		with open(output_file, 'r') as f:
			lines = f.read().splitlines()
			# Try to parse runtime statistics.
			# Time stats are three lines from the end.
			if len(lines) >= 3:
				time_line = lines[-3]
				if RE_TIME.match(time_line) and is_success:
					# Success, we found time!
					time = str(RE_TIME.match(time_line).group(1))
					print("Success. Elapsed: ", time)
					TIMES.write(name + ", " + phenotype + ", " + time + "\n")
					AGGREGATION_LIST.append(float(time))
				else:
					# Fail: output exists but does not have
					# correct time format.
					print("Fail. Last line of output:")
					print(lines[-1])
					TIMES.write(name + ", " + phenotype + ", " + "fail" + "\n")
			elif len(lines) > 0:
				# Fail: There is some output, but not enough
				# for a successful process.
				print("Fail. Last line of output:")
				print(lines[-1])
				TIMES.write(name + ", " + phenotype + ", " + "fail" + "\n")
			else:
				# Fail: There is no output.
				print("Fail. No output found.")
				TIMES.write(name + ", " + phenotype + ", " + "fail" + "\n")
		TIMES.flush()


	with open("phentoype_benchmark/benchmark.json") as handle:
		benchmark_definition = json.load(handle)

	BENCHMARKS = []
	for model, definition in benchmark_definition.items():
		for pn, p in definition["targets"].items():
			BENCHMARKS.append(BenchmarkDefinition(model, definition["file"], definition["vars"], pn, p))

	BENCHMARKS = sorted(BENCHMARKS, key=lambda x: x.size)
	print(len(BENCHMARKS))

	if TIMEOUT == 'none':
		code = os.system('timeout --help > /dev/null 2>&1')
		if code == 0:
			TIMEOUT = 'timeout'
			print("Timeout utility ok.")

	if TIMEOUT == 'none':
		code = os.system('gtimeout --help > /dev/null 2>&1')
		if code == 0:
			TIMEOUT = 'gtimeout'
			print("Timeout utility ok.")

	if TIMEOUT == 'none':
		print('ERROR: No timeout utility found.')
		exit()

	if PARALLEL > 0:
		ACTIVE = []
		while len(ACTIVE) > 0 or len(BENCHMARKS) > 0:
			while len(ACTIVE) < PARALLEL and len(BENCHMARKS) > 0:
				bench = BENCHMARKS.pop(0)
				name = bench.model_name
				phenotype = bench.phenotype_name
				output_file = f'{bench.model_name}_{bench.phenotype_name}.out'
				command = TIMEOUT + " " + CUT_OFF + " time -p " + SCRIPT + " " + bench.model_name + " " + bench.phenotype_name + " > " + output_file + " 2>&1"
				process = Process(target=SPAWN, args=(command,))
				process.start()
				ACTIVE.append((process, name, phenotype, output_file))
			time.sleep(1)  # Sleep 1s
			STILL_ACTIVE = []
			for (process, name, phenotype, output_file) in ACTIVE:
				if process.is_alive():
					STILL_ACTIVE.append((process, name, phenotype, output_file))
				else:
					PROCESS_RESULT(process, name, phenotype, output_file)
			ACTIVE = STILL_ACTIVE


