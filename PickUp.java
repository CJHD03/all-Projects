/** Name: CJ
 * Section: CSC 331
 * Date: 4/17/2023
 * Purpose: Creates PickUp Option for GUI/ calculates vehicle cost
 * */



package com.example.finaltransportation;

//subclass
public class PickUp extends Cost{
    private double miles;
    private final double mpg = 18, gasCost = 3.5;

    public PickUp(double miles){
        this.miles = miles;
    }

    public int getWeight_limit(){
        return 1980;}
    public double getGasCost(){return gasCost;}

    public double getVehicleCosts(){
        return (miles/mpg)*gasCost+ 25;//25 is the base cost for the pickup
    }
}