/** Name: CJ
 * Section: CSC 331
 * Date: 4/17/2023
 * Purpose: Creates Truck15Foot Option for GUI/ calculates vehicle cost
 * */

package com.example.finaltransportation;

//subclass
public class Truck15Foot extends Cost{
    private double miles;
    private final double mpg = 10, gasCost = 3.5;


    public Truck15Foot(double miles){
        this.miles = miles;
    }

    //getters
    public int getWeight_limit(){
        return 5605;}
    public double getGasCost(){return gasCost;}

    public double getVehicleCosts(){
        return (miles/mpg)*gasCost+ 75;//25 is the base cost for the van
    }
}