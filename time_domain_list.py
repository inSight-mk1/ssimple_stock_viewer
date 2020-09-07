
def find_closest_element(element, eles, up: bool, thresh):
    """ find matched car in n-before frame, used to estimate speed in a float time domain list

    Args:
        element: the car distance to original point currently
        eles: a list of car distances in n-before frame
        up: running direction of car
        thresh: max distance between now and n-before frame to prevent matching to a different car

    Returns:
        2-elements tuple, matched car distance to original point and running distance while n frames
    """
    min_distance = 9999
    min_element = None
    for ele in eles:
        if up:
            distance = ele - element
        else:
            distance = element - ele
        if 0 < distance < min_distance:
            min_distance = distance
            min_element = ele
    if min_distance > thresh:
        min_element = None
    return min_element, min_distance


class TimeDomainList(object):
    """ Define a list to record some results (can be any type) in the last n frames and provide speed estimate function

    Attributes:
        element_cnt: record how many frames' results
        list: a list to save the time domain data
    """
    def __init__(self, element_cnt=9):
        self.element_cnt = element_cnt
        self.list = [None] * element_cnt

    def push(self, element):
        """ put data to time domain list, put current data to the last position in the list

        Args:
            element: data need to push

        Returns:
            list after data pushed
        """
        for i in range(self.element_cnt - 1):
            self.list[i] = self.list[i+1]
        self.list[-1] = element
        return self.list

    def speed_estimate(self, up: bool, frame_interval=1/25, thresh=5.0):
        """ estimate all cars' speed in one lane

        Args:
            up: car direction
            frame_interval: interval (unit: meter) between two frames, equal to 1/fps
            thresh: max distance between now and n-before frame to prevent matching to a different car

        Returns:
            list of speed in one lane
        """
        current_distances = self.list[-1]
        speeds = []
        for dist in current_distances:
            speed = None
            previous_distances = self.list[0]
            if previous_distances is not None:
                min_element, min_distance = find_closest_element(dist, previous_distances, up, thresh=thresh)
                if min_element is not None:
                    travel_distance = min_distance
                    travel_time = frame_interval * (self.element_cnt - 1)
                    speed = travel_distance / travel_time * 3.6  # *3.6 convert m/s to kph
            speeds.append(speed)

        return speeds


if __name__ == '__main__':
    tdlist = TimeDomainList()
    print(tdlist.push(3))
    print(tdlist.push(4))
    print(tdlist.push(1))
