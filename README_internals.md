### Part-B: B2c - Dangerous Patterns
Bug-1: 
self.save() is used inside validate function, whereas the actual lifecycle is save() -> validate() -> before_save(), according to this existing code, it leads to a infinite loop inbetween validate() and save().

Bug-2:
