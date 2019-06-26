import time


def tms_to_str(tm):
    ''' tms_to_str onvertie la durée tm exprimée en ms en une chaîne exprimée
        en nombre d'heures, minutes et secondes
    '''
    ret = ""
    sec, ms = divmod(tm, 1000)
    if sec:
        min, sec = divmod(sec, 60)
        if min:
            hour, min = divmod(min, 60)
            if hour:
                ret += (str(hour).zfill(2) + "h")
            ret += (str(min).zfill(2) + "min")
    ret += str(sec).zfill(2) + "s"
    return ret


class Timer:
    def __init__(self, start=True):
        self.start = 0
        if start:
            self.run()

    def restart(self):
        self.start = time.time()

    def run(self):
        if not self.start:
            self.restart()
        else:
            raise Exception("The timer is always in running.")

    def elapsed(self):
        '''
            Retourne le temps écoulé en ms
        '''
        if self.start:
            return int(round((time.time() - self.start) * 1000))
        return 0

    def stop(self):
        elapsed = 0
        if self.start:
            elapsed = self.elapsed()
            self.start = 0
        return elapsed

    def __repr__(self):
        tm = self.elapsed()

        return tms_to_str(tm)

if __name__ == '__main__':
    tm = Timer()
    for _ in range(10):
        print(tm, end= " ", flush=True)
        time.sleep(1)
    print()
