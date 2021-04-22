def main():

    from game_mk2 import Snake
    import time
    from multiprocessing import Process

    desired_inscances = 2
    instance = 0
    objects = {}
    processes = {}
    while instance < desired_inscances: 
         objects["p{0}".format(instance)] = Snake(instance)
         processes["p{0}".format(instance)] = Process(target=objects["p{0}".format(instance)].run_game)
         processes["p{0}".format(instance)].start()
         instance += 1
         


if __name__ == "__main__":
    main()