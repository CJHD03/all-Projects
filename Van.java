/** Name: CJ
 * Section: CSC 331
 * Date: 4/17/2023
 * Purpose: Creates Van Option for GUI/ calculates vehicle cost
 * */



package com.example.finaltransportation;

//subclass
public class Van extends Cost{
    private double miles;
    private final double mpg = 18, gasCost = 3.5;

    public Van(double miles){
        this.miles = miles;
    }

    //getters
    public int getWeight_limit(){
        return 4000;}
    public double getGasCost(){return gasCost;}

    public double getVehicleCosts(){
        return (miles/mpg)*gasCost + 25;//25 is the base cost for the van
    }
}