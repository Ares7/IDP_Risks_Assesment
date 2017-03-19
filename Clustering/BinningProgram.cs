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

        double[] rawData = new double[20] { 
          66, 66, 66, 67, 67, 67, 67, 68, 68, 69,
          73, 73, 73, 74, 76, 78,
          60, 61, 62, 62 };

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
        double[] newData = new double[6] { 62.0, 66.0, 73.0, 59.5, 75.5, 80.5 };
 
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
