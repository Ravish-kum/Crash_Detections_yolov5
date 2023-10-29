import math

LANE_CARS_THRESHOLD = 10
METER_PER_PIXEL = 0.5
SPEED_THRESHOLD = 100

class TrackingOperations:
    def checks_calling(self, operational_tracking, object_id, no_of_objects_in_frame):
        alert0, alert1, alert2 = None, None, None
        if operational_tracking:
            warning = self.heavy_traffic(no_of_objects_in_frame)
            alert0 =self.high_speeding(operational_tracking,object_id)
            alert1 = self.wrong_side_driving(operational_tracking,object_id)
            alert2 = self.crashed_car_by_no_motion(operational_tracking, object_id)
            if alert0 or alert1 or alert2:
                return print([warning, alert0, alert1, alert2])
            
    def heavy_traffic(self, no_of_objects_in_frame):              # warning heavy traffic
        if(len(no_of_objects_in_frame) >= LANE_CARS_THRESHOLD):
            return "[Warning] Heavy Traffic"
            
    def high_speeding(self,operational_tracking,object_id):        # level one alert
        #print(operational_tracking)
        frames_to_calculate_from = 6
        estimated_speed = ((operational_tracking[frames_to_calculate_from - 1][1] - operational_tracking[0][1])*METER_PER_PIXEL)/((len(operational_tracking)-4)/24)
        #print(estimated_speed)
        if(estimated_speed >= SPEED_THRESHOLD):
            return "Level 0 Alert: Speeding Car", object_id

    def wrong_side_driving(self,operational_tracking, object_id):   # level second alert
        for i in range(len(operational_tracking)-1):
            if  operational_tracking[i][1] < operational_tracking[i+1][1]:
                continue
            else:
                return "Level 2 Alert: Wrong Side Driving",object_id

    def crashed_car_by_no_motion(self,operational_tracking,object_id):   # level third alert
        error_estimation = 0
        for i in range(len(operational_tracking)-1):
            if  operational_tracking[i] == operational_tracking[i+1]:
                error_estimation += 1
            else:
                continue
        
        if error_estimation > 5 :
            return "Level 3 Alert: Car Crash",object_id
        
    

class CentroidTracker(TrackingOperations):
    def __init__(self):
        self.tracking_objects = {}
        self.track_id = 0
        self.operational_tracking = {}  
    
    def appending(self, object_id, pt):

        if len(self.operational_tracking[object_id]) == 10:
            self.operational_tracking[object_id] = self.operational_tracking[object_id][1:]
            self.operational_tracking[object_id].append(pt)
            self.checks_calling(self.operational_tracking[object_id],object_id, self.operational_tracking)
        else:
            self.operational_tracking[object_id].append(pt)
        
        #print(self.operational_tracking)


    def register(self, center_pt_current_frame, center_pt_previous_frame, count):
        # Register a new object by assigning a unique ID
        #print('here count',count)
        
        if count <= 2:
            print("Ss",center_pt_current_frame)
            print("gmae",center_pt_previous_frame)

            for pt in center_pt_current_frame:
                for pt2 in center_pt_previous_frame:
                    distance = math.sqrt(math.pow((pt2[0] -pt[0]),2)+math.pow(( pt2[1] - pt[1]),2))
                    #print("distacne", int(distance))
                    if int(distance) < 35:
                        self.tracking_objects[self.track_id] = pt
                        #print('track',self.tracking_objects)
                        self.operational_tracking[self.track_id] = [pt]
                        #print('operational',self.operational_tracking)
                        self.track_id += 1
                    # if distance is 0 there is a possibilty of a stopped car
        else:
            
            tracking_objects_copy = self.tracking_objects.copy()
            center_pt_current_frame_copy = center_pt_current_frame.copy()
            for object_id, pt2 in tracking_objects_copy.items():
                object_exists= False
                for pt in center_pt_current_frame_copy:
                    distance = math.sqrt(math.pow((pt2[0] -pt[0]),2)+math.pow(( pt2[1] - pt[1]),2))
                    #print("22distacne",int(distance))
                    if int(distance) < 35:
                        self.tracking_objects[object_id] = pt
                        #print('trackkkk    ',self.tracking_objects)
                        object_exists = True
                        if object_id in self.operational_tracking:
                            self.appending(object_id, tuple(pt))
                        #print('operations trackkk   ',self.operational_tracking)
                        try:
                            center_pt_current_frame.remove(pt)
                        except:
                            pass
                        
                        continue

                if not object_exists:
                    self.tracking_objects.pop(object_id)
                    self.operational_tracking.pop(object_id)


            for pt in center_pt_current_frame:
                self.tracking_objects[self.track_id] = pt
                self.operational_tracking[self.track_id] = [tuple(pt)]
                self.track_id += 1
                
        return self.tracking_objects
  