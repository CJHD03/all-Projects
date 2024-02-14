/** Name: CJ
 * Section: CSC 331
 * Date: 4/17/2023
 * Purpose: Creates Truck26Foot Option for GUI/ calculates vehicle cost
 * */

package com.example.finaltransportation;

//subclass
public class Truck26Foot extends Cost{
    private double miles;
    private final double mpg = 10, gasCost = 3.5;


    public Truck26Foot(double miles){
        this.miles = miles;
    }

    //getters
    public int getWeight_limit(){
        return 9600;}
    public double getGasCost(){return gasCost;}

    public double getVehicleCosts(){
        return (miles/mpg)*gasCost + 125;//125 is the base cost for the van
    }
}