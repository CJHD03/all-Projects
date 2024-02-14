/** Name: CJ
 * Section: CSC 331
 * Date: 4/17/2023
 * Purpose: Creates Truck10Foot Option for GUI/ calculates vehicle cost
 * */




package com.example.finaltransportation;

//subclass
public class Truck10Foot extends Cost{
    private double miles;
    private final double mpg = 12, gasCost = 3.5;


    public Truck10Foot(double miles){
        this.miles = miles;
    }

    //getters
    public int getWeight_limit(){
        return 2810;}
    public double getGasCost(){return gasCost;}

    public double getVehicleCosts(){
        return (miles/mpg)*gasCost+ 50;//25 is the base cost for the van
    }
}