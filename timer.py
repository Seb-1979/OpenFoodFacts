import time


class Timer:
    def __init__(self, start=True):
        self.start = 0
        if start:
            self.start = self.run()

    def restart(self):
        self.start = time.time()

    def run(self):
        if not self.start:
            return self.restart()
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

    def __str__(self):
        tm = self.elapsed()
        ret = ""
        sec, ms = divmod(tm, 1000)
        if sec:
            min, sec = divmod(sec, 60)
            if min:
                hour, min = divmod(min, 60)
                if hour:
                    ret += (str(hour) + "h")
                ret += (str(min) + "min")
        ret += (str(sec + ms/1000) + "s")

        return ret
