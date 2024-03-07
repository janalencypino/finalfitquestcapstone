class ExerciseDetails:
    def __init__(self,
                 exer_name: str,
                 exer_reps: int,
                 exer_sets: int,
                 exer_dur : int,
                 exer_desc: str,
                 body_arr : list[str] = None,
                 angle_arr: list[float] = None,
                 img_path : str = ""):
        self.name           = exer_name
        self.reps           = exer_reps
        self.sets           = exer_sets
        self.duration       = exer_dur
        self.description    = exer_desc
        self.body           = body_arr
        self.angle          = angle_arr
        self.img_path       = img_path
        self.is_copy        = False
        self.check          = None

    def set_exercise_dict_params(self,
                                 body_arr: list[str] = None,
                                 angle_arr: list[float] = None):
        if (body_arr is not None):
            setattr(self, 'body', body_arr)

        if (angle_arr is not None):
            setattr(self, 'angle', angle_arr)

    def convert(exer_dict):
        object          = ExerciseDetails(
            exer_name   = exer_dict['name'],
            exer_reps   = exer_dict['reps'],
            exer_sets   = exer_dict['sets'],
            exer_dur    = exer_dict['duration'],
            exer_desc   = exer_dict['description'],
            img_path    = (exer_dict['image_path']) or "",
        )
        body, angle     = [], []
        for key, value in exer_dict.items():
            if key[0:8] == 'bodypart':
                body.append(value)
            if key[0:5] == 'angle':
                angle.append(value)

        object.set_exercise_dict_params(body, angle)
        return object
    
    def copy(self):
        _obj_copy   = ExerciseDetails(self.name,
                                      self.reps,
                                      self.sets,
                                      self.duration,
                                      self.description,
                                      self.body,
                                      self.angle,
                                      self.img_path)
        _obj_copy.check     = self.check
        _obj_copy.is_copy   = True
        _obj_copy.base      = self
        return _obj_copy
    
    def inherit(self, base):
        '''
        base is of type ExerciseDetails
        '''
        if not isinstance(base, ExerciseDetails):
            return
        
        self.name           = base.name
        self.duration       = base.duration * self.reps / base.reps
        self.description    = base.description
        self.body           = base.body[:]
        self.angle          = base.name
        self.img_path       = base.img_path
        self.check          = base.check
