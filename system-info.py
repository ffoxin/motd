import subprocess
from collections import defaultdict, namedtuple
from operator import itemgetter

import click
import tabulate

LoadavgStats = namedtuple("LoadavgStats", ("avg1", "avg5", "avg10", "processes"))
MemoryStats = namedtuple("MemoryStats", ("total", "used", "free"))
FilesystemStats = namedtuple(
    "FilesystemStats",
    ("filesystem", "blocks", "used", "available", "use_pcnt", "mount"),
)
ContainerStats = namedtuple("ContainerStats", ("name", "ip", "project", "status"))


def main():
    with open("/proc/loadavg") as file:
        result = file.read().split()
    load_avg = LoadavgStats(*result[:4])
    # print(load_avg)

    result = subprocess.run(
        "free -m", shell=True, text=True, capture_output=True
    ).stdout.split("\n")
    mem = MemoryStats(*result[1].split()[1:4])
    swap = MemoryStats(*result[2].split()[1:4])
    # print(mem)
    # print(swap)

    result = subprocess.run(
        "vcgencmd measure_temp", shell=True, text=True, capture_output=True
    ).stdout
    video_temperature = result[result.find("=") + 1 : result.find("'")]
    # print(video_temperature)

    result = subprocess.run("df", shell=True, text=True, capture_output=True).stdout
    filesystems = [FilesystemStats(*fs.split()) for fs in result.split("\n")[1:] if fs]
    overused = [fs for fs in filesystems if 100.0 * int(fs.used) / int(fs.blocks) > 85]
    # print(overused)

    result = subprocess.run(
        "docker inspect --format='{{.Name}}\t{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}\t{{index .Config.Labels \"com.docker.compose.project\"}}\t{{.State.Status}}' $(docker ps -aq)",
        shell=True,
        text=True,
        capture_output=True,
    ).stdout
    container_stats = [
        ContainerStats(*cs.split("\t")) for cs in result.split("\n") if cs
    ]
    projects = defaultdict(list)
    for cs in container_stats:
        projects[cs.project].append(cs)
    list_containers = []
    for project, containers in sorted(projects.items(), key=itemgetter(0)):
        for index, cs in enumerate(containers):
            if cs.status == "running":
                fg = "green"
            elif cs.status == "exited":
                fg = "red"
            else:
                fg = "yellow"
            list_containers.append(
                [
                    "",
                    project if index == 0 else "",
                    click.style("●", fg=fg),
                    cs.name[1:],
                    cs.ip,
                ]
            )

    # print(projects)

    click.echo(f"  System load:      {load_avg.avg10}")
    click.echo(
        f"  Memory usage:     {100. * int(mem.used) / (int(mem.total) or 1):.0f}"
    )
    click.echo(
        f"  Swap usage:       {100. * int(swap.used) / (int(swap.total) or 1):.0f}"
    )
    click.echo(f"  RPI Temperature:  {video_temperature}")
    click.echo("")
    # click.echo(f"  Containers:")
    click.echo(
        tabulate.tabulate(
            list_containers,
        )
    )


if __name__ == "__main__":
    main()
