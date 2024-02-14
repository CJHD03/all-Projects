/** Name: Zach, CJ, Evan
 * Section: CSC 331
 * Date: 4/17/2023
 * Purpose: Define various costs for the GUI, calculates the partial total cost,
 * */



package com.example.finaltransportation;
//super class
public class Cost{
    private final int insurance = 1000;
    private double mileage;//how far we need to go
    private boolean movers;
    private boolean halfDayorFullDay; //true for half day, false for full day

    //Constructor
    public Cost(double mileage, boolean movers, boolean halfDayorFullDay){
        this.mileage = mileage;
        this.movers = movers;
        this.halfDayorFullDay = halfDayorFullDay;
    }
    //empty constructor
    public Cost() {

    }

    //Getters
    public double getCancellationFee(){
        //instance variables
        return 100;}
    public double getMileage(){return this.mileage;}
    public boolean getMovers(){return this.movers;}
    public boolean getHalfDayorfullDay(){return this.halfDayorFullDay;}
    public int getInsurance() {return insurance;}


    //Setters
    public void setMileage(double mileage){this.mileage = mileage;}
    public void setMovers(boolean movers){this.movers = movers;}
    public void setHalfDayorfullDay(boolean halfDayorFullDay){this.halfDayorFullDay = halfDayorFullDay;}

    public int calcStaffCost(){ //calculates cost for if you arent doing a self move in. 300 for halfday, 400 for full day
        if (this.movers){
            if (this.halfDayorFullDay){
                return 300;
            } else{
                return 400;
            }
        } else{
            return 0;
        }
    }
}