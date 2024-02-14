/** Name: Zach
 * Section: CSC 331
 * Date: 4/17/2023
 * Purpose: Creates Time variables for GUI/ Calculates End Time for GUI
 * */

package com.example.finaltransportation;

public class Time extends Cost{
    //Instance Variable
    private int startTime;
    private boolean HorF;

    //Constructor
    public Time(int startTime, boolean HorF){
        this.HorF = HorF;
        this.startTime = startTime;
    }

    //Getter
    public int getStartTime(){return this.startTime;}

    //Setter
    public void setStartTime(int startTime){this.startTime = startTime;}

    //Calculates End Time
    public int calcEndTime(){ //calculates end time and modfies for if it goes to a new day
        if (this.HorF){
            //Calc end time for half day
            return (startTime+600)%2400;
        } else{
            //Calc end time for full day
            return (startTime+1000)%2400;
        }
    }
}