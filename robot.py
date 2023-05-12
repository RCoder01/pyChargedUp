from robotpy_ext.misc.asyncio_policy import FPGATimedEventLoop
import asyncio
import wpilib
import ctre

AUTONOMOUS_TIME_PER_LOOP = 0.015
class Robot(wpilib.TimedRobot):
    def robotInit(self) -> None:
        self.motor_0 = ctre.WPI_TalonFX(0)
        self.motor_1 = ctre.WPI_TalonFX(1)
        self.last_output = 0

    def teleopPeriodic(self) -> None:
        self.motor_0.set(ctre.ControlMode.PercentOutput, self.last_output)
        self.last_output = min(self.last_output + 0.001, 1)

    async def create_auto(self):
        self.auto_task = asyncio.create_task(self.autonomous()),

    def autonomousInit(self) -> None:
        self.async_runner = asyncio.Runner(loop_factory=FPGATimedEventLoop).__enter__()
        self.async_runner.run(self.create_auto())

    async def async_run_auto(self) -> None:
        _, self.auto_task = await asyncio.wait(self.auto_task, timeout=AUTONOMOUS_TIME_PER_LOOP)

    def autonomousPeriodic(self) -> None:
        wpilib.SmartDashboard.putBoolean('auto func', bool(self.auto_task))
        if self.auto_task:
            self.async_runner.run(self.async_run_auto())
            if not self.auto_task:
                self.autonomous_cleanup()

    def autonomousExit(self) -> None:
        self.async_runner.close()
        if self.auto_task:
            self.autonomous_cleanup()

    def autonomous_cleanup(self) -> None:
        print('Auto cleanup')
        self.motor_0.set(ctre.ControlMode.PercentOutput, 0)
        self.motor_1.set(ctre.ControlMode.PercentOutput, 0)

    async def autonomous(self) -> None:
        from datetime import datetime
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self.set_motor_0(1))
            tg.create_task(self.set_motor_1(1))
        asyncio.create_task
        await asyncio.sleep(1)
        await self.set_motor_1(0.5)
        await asyncio.sleep(1)
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self.ramp_motor_0(2))
            tg.create_task(self.set_motor_1(1))
        await asyncio.sleep(1)


    async def set_motor_0(self, power: float) -> None:
        await asyncio.sleep(2) # Stand-in for a state that takes time to reach
        self.motor_0.set(ctre.ControlMode.PercentOutput, power)

    async def set_motor_1(self, power: float) -> None:
        await asyncio.sleep(1) # Stand-in for a state that takes time to reach
        self.motor_1.set(ctre.ControlMode.PercentOutput, power)

    async def ramp_motor_0(self, time: float) -> None:
        start = wpilib.Timer.getFPGATimestamp()
        while True:
            await asyncio.sleep(AUTONOMOUS_TIME_PER_LOOP)
            completion = (wpilib.Timer.getFPGATimestamp() - start) / time
            if completion > 1:
                self.motor_0.set(ctre.ControlMode.PercentOutput, 1)
                return
            self.motor_0.set(ctre.ControlMode.PercentOutput, completion)

if __name__ == '__main__':
    wpilib.run(Robot)
