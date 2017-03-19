using System;
using System.Collections.Generic;
namespace BinningData
{
  class BinningProgram
  {
    static void Main(string[] args)
    {
      try
      {
        Console.WriteLine("\nBegin discretization of continuous data demo\n");

        double[] rawData = new double[201] { 
          
-4.43
,-3.32
,-21.02
,-8.3
,-0.93
,-6.9
,-99.64
,-26.62
,-142.84
,-333.61
,-28.03
,-40.23
,-42.47
,-1.57
,-19.95
,-28.11
,-36.29
,-108.89
,-16.52
,-261.09
,-42.66
,-5.23
,-396.36
,-2.81
,-1.28
,-23.83
,-203.38
,-0.36
,-0.33
,-16.33
,-3.32
,-253.51
,-1223.71
,-189.94
,-109.62
,-102.67
,-0.3
,-173.17
,-176.43
,-20.77
,-47.2
,-263.82
,-75.19
,-106.05
,-3.47
,-2.12
,-210.15
,-177.82
,-24.05
,-583.58
,-289.49
,-245.2
,-59.24
,-118.86
,-127.46
,-14.45
,-62.07
,-53.96
,-4.78
,-203.45
,-249.04
,-0.53
,-72.5
,-128.96
,-15.87
,-12.14
,-139.81
,-23.79
,-66.03
,-31.48
,-219.96
,-6.88
,-28.38
,-66.75
,-16.07
,-23.66
,-30.77
,-118.85
,-7.68
,-540.6
,-139.45
,-106.76
,-95.58
,-19.58
,-5.4
,-191.51
,-91.17
,-4.72
,-15.94
,-29.84
,-73.87
,-12.43
,-74.36
,-80.12
,-203.8
,-76.21
,-33.3
,-64.43
,-37.57
,-71.77
,-18.76
,-17.47
,-52.66
,-20.71
,-147.04
,-33.77
,-68.13
,-76.47
,-221.01
,-164.31
,-126.43
,-131.33
,-247.11
,-39.98
,-30.1
,-22.29
,-46.53
,-32.6
,-94.26
,-59.1
,-23.65
,-43.63
,-73.16
,-63.13
,-2.56
,-65.76
,-42.34
,-3.19
,-35.94
,-29.7
,-84.8
,-80.85
,-14.04
,-28.05
,-22.32
,-14.96
,-138.98
,-41.48
,-15.48
,-31.36
,-10.63
,-127.72
,-63.65
,-179.51
,-199.79
,-30.56
,-73.66
,-1.9
,-2.44
,-92.64
,-83.95
,-148.3
,-3126.49
,-35.97
,-176
,-53.55
,-117.18
,-118.79
,-101.08
,-5.64
,-176.52
,-165.57
,-480.05
,-457.34
,-0.49
,-50.31
,-18.26
,-249.36
,-21.07
,-70.43
,-95.94
,-22.02
,-220.81
,-8.24
,-15.95
,-119.06
,-197.83
,-230.24
,-208.95
,-41
,-320.38
,-10.33
,-66.1
,-194.74
,-253.84
,-389.49
,-27.94
,-80.45
,-112.62
,-5.52
,-46.77
,-55.81
,-86.96
,-6.51
,-8.1
,-18.92
,-152.86
,-308.77
,-10.28
,-13.36
,-42.84
 };

        Console.WriteLine("Raw data:");
        ShowVector(rawData, 2, 10);

        Console.WriteLine("\nCreating a discretizer on the raw data");
        Discretizer d = new Discretizer(rawData);
        Console.WriteLine("\nDiscretizer creation complete");

        Console.WriteLine("\nDisplaying internal structure of the discretizer:\n");
        Console.WriteLine("-------------------------------------------------------------\n");
        Console.WriteLine(d.ToString());
        Console.WriteLine("\n-------------------------------------------------------------");

        Console.WriteLine("\nGenerating three existing and three new data values");
        double[] newData = new double[1] { 1.0};
 
        Console.WriteLine("\nData values:");
        ShowVector(newData, 2, 10);

        Console.WriteLine("\nDiscretizing the data:\n");
        for (int i = 0; i < newData.Length; ++i)
        {
          int cat = d.Discretize(newData[i]);
          Console.WriteLine(newData[i].ToString("F2") + " -> " + cat);
        }

        Console.WriteLine("\n\nEnd discretization demo");
        Console.ReadLine();
      }
      catch (Exception ex)
      {
        Console.WriteLine(ex.Message);
        Console.ReadLine();
      }

    } // Main

    public static void ShowVector(double[] vector, int decimals, int itemsPerRow)
    {
      for (int i = 0; i < vector.Length; ++i)
      {
        if (i % itemsPerRow == 0) Console.WriteLine("");
        Console.Write(vector[i].ToString("F" + decimals) + " ");
      }
      Console.WriteLine("");
    }
  } // Program

  public class Discretizer
  {
    private double[] data; // sorted copy of distinct raw numeric data
    private int k; // number of clusters = number of categories. must be > data.Length
    private double[] means; // average of pts in each cluster, from sums[] and counts[]
    private int[] clustering; // index = index into data[], value = cluster ID 

    public Discretizer(double[] rawData)
    {
      double[] sortedRawData = new double[rawData.Length];
      Array.Copy(rawData, sortedRawData, rawData.Length);
      Array.Sort(sortedRawData);
      this.data = GetDistinctValues(sortedRawData);
      this.clustering = new int[data.Length];

      this.k = (int)Math.Sqrt(data.Length); // heuristic

      this.means = new double[k];
      this.Cluster();
    }

    private static double[] GetDistinctValues(double[] array)
    {
      List<double> distinctList = new List<double>();
      distinctList.Add(array[0]);
      for (int i = 0; i < array.Length - 1; ++i)
        if (AreEqual(array[i], array[i + 1]) == false)
          distinctList.Add(array[i + 1]);

      double[] result = new double[distinctList.Count];
      distinctList.CopyTo(result);
      return result;
    }

    private static bool AreEqual(double x1, double x2)
    {
      if (Math.Abs(x1 - x2) < 0.000001) return true;
      else return false;
    }

    public int Discretize(double x)
    {
      // for any value x, compute distance to each cluster mean,
      // return closest index, which is a cluster, which is the category
      double[] distances = new double[k];
      for (int c = 0; c < k; ++c)
        distances[c] = Distance(x, means[c]);
      return MinIndex(distances);
    }

    public override string ToString()
    {
      string s = "";
      s += "Distinct data:";
      for (int i = 0; i < data.Length; ++i)
      {
        if (i % 10 == 0) s += "\n";
        s += data[i].ToString("F2") + " ";
      }
      s += "\n\nk = " + k;
      s += "\n\nClustering:\n";
      for (int i = 0; i < clustering.Length; ++i)
        s += clustering[i] + " ";
      s += "\n\nMeans:\n";
      for (int i = 0; i < means.Length; ++i)
        s += means[i].ToString("F2") + " ";
      return s;
    }

    // ================================

    private void InitializeClustering()
    {
      int[] initialIndexes = GetInitialIndexes();
      for (int di = 0; di < data.Length; ++di)
      {
        int c = InitialCluster(di, initialIndexes);
        clustering[di] = c;
      }
    }

    private int[] GetInitialIndexes()
    {
      // assumes data is sorted
      int interval = data.Length / k;
      int[] result = new int[k];
      for (int i = 0; i < k; ++i)
        result[i] = interval * (i + 1);
      return result;
    }

    private int InitialCluster(int di, int[] initialIndexes)
    {
      // for data index di (like 5) and a set of initial indexes (like 2,4,6) what cluster?
      for (int i = 0; i < initialIndexes.Length; ++i)
        if (di < initialIndexes[i])
          return i; // assumes initialIndexes are ordered
      return initialIndexes.Length - 1; // last cluster
    }

    private void Cluster()
    {
      InitializeClustering();
      ComputeMeans();

      bool changed = true;
      bool success = true;
      int ct = 0;
      int maxCt = data.Length * 10; // heuristic
      while (changed == true && success == true && ct < maxCt)
      {
        ++ct;
        changed = AssignAll();
        success = ComputeMeans();
      }
    }

    private bool ComputeMeans()
    {
      // return false if at some point a count goes to zero
      double[] sums = new double[k];
      int[] counts = new int[k];

      for (int i = 0; i < data.Length; ++i)
      {
        int c = clustering[i]; // cluster ID
        sums[c] += data[i];
        counts[c]++;
      }

      for (int c = 0; c < sums.Length; ++c)
      {
        if (counts[c] == 0)
          return false; // serious algorithm problem
        else
          sums[c] = sums[c] / counts[c];
      }

      sums.CopyTo(this.means, 0);
      return true; // all means computed successfully
    }

    private bool AssignAll()
    {
      // scan data, assign all data (indexes) to a cluster, return true if any changes
      bool changed = false;
      double[] distances = new double[k]; // distance to each cluster mean
      for (int i = 0; i < data.Length; ++i)
      {
        for (int c = 0; c < k; ++c)
          distances[c] = Distance(data[i], means[c]);
        int newCluster = MinIndex(distances);
        if (newCluster != clustering[i])
        {
          changed = true;
          clustering[i] = newCluster;
        }
      }
      return changed;
    }

    private int MinIndex(double[] distances)
    {
      int indexOfMin = 0;
      double smallDist = distances[0];
      for (int k = 0; k < distances.Length; ++k)
      {
        if (distances[k] < smallDist)
        {
          smallDist = distances[k];
          indexOfMin = k;
        }
      }
      return indexOfMin;
    }

    private static double Distance(double x1, double x2)
    {
      return Math.Sqrt((x1 - x2) * (x1 - x2));
    }

  } // class

} // ns

