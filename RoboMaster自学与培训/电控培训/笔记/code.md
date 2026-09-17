```
class Motor
{
int id{0};
double maxRpm{0};
double targetRpm{0};
double currentRpm{0};
double output{0};
bool enabled{0};
public:
Motor(int motorid, double maximumRpm) : id(motorid), maxRpm(maximumRpm)
{
}
void enable();
void disable();
bool setTargetRpm(double rpm);
void updateCurrentRpm(double rpm);
double calculatePOutput(double kp);
bool isEnabled() const;
double getTargetRpm() const;
double getCurrentRpm() const;
double getOutput() const;
void printStatus() const;
};

```



