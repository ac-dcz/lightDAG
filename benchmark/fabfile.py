from fabric import task

from benchmark.local import LocalBench
from benchmark.logs import ParseError, LogParser
from benchmark.utils import BenchError,Print
from alibaba.instance import InstanceManager
from alibaba.remote import Bench
@task
def local(ctx):
    ''' Run benchmarks on localhost '''
    bench_params = {
        'nodes': 4,
        'duration': 10,
        'rate': 2_000,                  # tx send rate
        'batch_size': 800,              # the max number of tx that can be hold 
        'log_level': 0b1111,            # 0x1 infolevel 0x2 debuglevel 0x4 warnlevel 0x8 errorlevel
        'protocol_name': "lightDAG"
    }
    node_params = {
        "pool": {
            # "rate": 1_000,              # ignore: tx send rate 
            "tx_size": 250,                # tx size
            # "batch_size": 200,          # ignore: the max number of tx that can be hold 
            "max_queue_size": 10_000 
	    },
        "consensus": {
            "sync_timeout": 500,        # node sync time
            "network_delay": 2_000,     # network delay
            "min_block_delay": 0,       # send block delay
            "ddos": False,              # DDOS attack
            "faults": 0,                # the number of byzantine node
            "retry_delay": 5_000        # request block period
        }
    }
    try:
        ret = LocalBench(bench_params, node_params).run(debug=True).result()
        print(ret)
    except BenchError as e:
        Print.error(e)


@task
def create(ctx, nodes=2):
    ''' Create a testbed'''
    try:
        InstanceManager.make().create_instances(nodes)
    except BenchError as e:
        Print.error(e)


@task
def destroy(ctx):
    ''' Destroy the testbed '''
    try:
        InstanceManager.make().terminate_instances()
    except BenchError as e:
        Print.error(e)

@task
def deleteConfig(ctx):
    ''' Destroy the testbed '''
    try:
        InstanceManager.make().delete_security()
    except BenchError as e:
        Print.error(e)

@task
def start(ctx, max=10):
    ''' Start at most `max` machines per data center '''
    try:
        InstanceManager.make().start_instances(max)
    except BenchError as e:
        Print.error(e)


@task
def stop(ctx):
    ''' Stop all machines '''
    try:
        InstanceManager.make().stop_instances()
    except BenchError as e:
        Print.error(e)

@task
def install(ctx):
    try:
        Bench(ctx).install()
    except BenchError as e:
        Print.error(e)

@task
def info(ctx):
    ''' Display connect information about all the available machines '''
    try:
        InstanceManager.make().print_info()
    except BenchError as e:
        Print.error(e)



@task
def remote(ctx):
    ''' Run benchmarks on AWS '''
    bench_params = {
        'nodes': [1],
        'node_instance': 4,               # the number of running instance for a node  (max = 4)
        'duration': 10,
        'rate': 2_000,                  # tx send rate
        'batch_size': [800],              # the max number of tx that can be hold 
        'log_level': 0b1111,              # 0x1 infolevel 0x2 debuglevel 0x4 warnlevel 0x8 errorlevel
        'protocol_name': "lightDAG",
        'runs': 1
    }
    node_params = {
        "pool": {
            # "rate": 1_000,              # ignore: tx send rate 
            "tx_size": 250,                # tx size
            # "batch_size": 200,          # ignore: the max number of tx that can be hold 
            "max_queue_size": 10_000 
	    },
        "consensus": {
            "sync_timeout": 500,        # node sync time
            "network_delay": 2_000,     # network delay
            "min_block_delay": 0,       # send block delay
            "ddos": False,              # DDOS attack
            "faults": 0,                # the number of byzantine node
            "retry_delay": 5_000        # request block period
        }
    }
    try:
        Bench(ctx).run(bench_params, node_params, debug=False)
    except BenchError as e:
        Print.error(e)



@task
def kill(ctx):
    ''' Stop any HotStuff execution on all machines '''
    try:
        Bench(ctx).kill()
    except BenchError as e:
        Print.error(e)

@task
def download(ctx,node_instance=4,ts="2024-06-04v10:15:10"):
    ''' download logs '''
    try:
        print(Bench(ctx).download(node_instance,ts).result())
    except BenchError as e:
        Print.error(e)

@task
def logs(ctx):
    ''' Print a summary of the logs '''
    # try:
    print(LogParser.process('./logs/2024-06-03v11:18:47').result())
    # except ParseError as e:
    #     Print.error(BenchError('Failed to parse logs', e))
