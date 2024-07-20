# Data Engineering
* clean up download code, make a library
* Compress/convert to parquet csv files

Yes, converting your CSV files to Parquet format and then analyzing the data using Dask in Python is a highly efficient approach. Here's a step-by-step guide to help you achieve this:

## Method 1: Convert CSV to Parquet
### Step-by-Step Guide

#### 1. Install Necessary Libraries

First, make sure you have the necessary Python libraries installed. You will need `pandas`, `pyarrow`, and `dask`.

```bash
pip install pandas pyarrow dask
```

#### 2. Convert CSV Files to Parquet

Create a script to convert all your CSV files to Parquet format. This script reads each CSV file, converts it to Parquet, and saves it.

```python
import os
import pandas as pd

input_folder = 'path/to/csv/folder'
output_folder = 'path/to/parquet/folder'

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

for filename in os.listdir(input_folder):
    if filename.endswith('.csv'):
        csv_path = os.path.join(input_folder, filename)
        parquet_path = os.path.join(output_folder, filename.replace('.csv', '.parquet'))
        
        df = pd.read_csv(csv_path)
        df.to_parquet(parquet_path, index=False, compression='snappy')

print("Conversion to Parquet completed.")
```

#### 3. Analyze Data Using Dask

Once your data is in Parquet format, you can use Dask to analyze it efficiently.

```python
import dask.dataframe as dd

# Read all Parquet files into a Dask DataFrame
parquet_files = 'path/to/parquet/folder/*.parquet'
ddf = dd.read_parquet(parquet_files)

# Example: Compute the mean of a column
mean_values = ddf['your_column'].mean().compute()
print(f'Mean values: {mean_values}')

# Example: Fit a statistical model (e.g., linear regression)
from dask_ml.linear_model import LinearRegression
from dask_ml.model_selection import train_test_split

# Prepare data
X = ddf[['feature1', 'feature2']].values
y = ddf['target'].values

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Initialize and fit the model
model = LinearRegression()
model.fit(X_train, y_train)

# Evaluate the model
score = model.score(X_test, y_test)
print(f'Model score: {score}')
```

### Benefits of This Approach

- **Storage Efficiency:** Parquet files are highly compressed, reducing storage requirements.
- **Memory Efficiency:** Dask allows you to work with data larger than your RAM by parallelizing operations and only loading necessary chunks into memory.
- **Performance:** Both Parquet and Dask are optimized for speed, making data processing and analysis faster compared to working directly with CSV files.

### Summary

1. **Convert CSV to Parquet:** This reduces storage space and speeds up read operations.
2. **Use Dask for Analysis:** Dask handles larger-than-memory datasets efficiently, allowing you to perform complex analyses and fit models without overloading your system's memory.

By following these steps, you'll be able to efficiently manage and analyze your large datasets without running into memory limitations.

## Method 2: Compress CSV files using gzip and use Dask
Using gzip to compress your CSV files and then reading them into Python for analysis is another viable approach. While gzip compression can significantly reduce storage space, it might not provide the same level of efficiency in terms of read performance and memory usage as Parquet format. However, it can still be a practical solution depending on your specific needs. Here's how you can achieve this:

### Step-by-Step Guide

#### 1. Install Necessary Libraries

Make sure you have the necessary Python libraries installed. You will need `pandas` and `dask`.

```bash
pip install pandas dask
```

#### 2. Compress CSV Files Using gzip

You can compress your CSV files using gzip either through the command line or using Python. Here’s how to do it using Python:

```python
import os
import gzip
import shutil

input_folder = 'path/to/csv/folder'
output_folder = 'path/to/gzip/folder'

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

for filename in os.listdir(input_folder):
    if filename.endswith('.csv'):
        csv_path = os.path.join(input_folder, filename)
        gzip_path = os.path.join(output_folder, filename + '.gz')
        
        with open(csv_path, 'rb') as f_in:
            with gzip.open(gzip_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

print("Compression to gzip completed.")
```

#### 3. Read and Analyze Compressed Files Using Dask

Dask can read gzip-compressed CSV files directly. Here’s how you can read these files and perform analysis:

```python
import dask.dataframe as dd

# Read all gzip-compressed CSV files into a Dask DataFrame
gzip_files = 'path/to/gzip/folder/*.gz'
ddf = dd.read_csv(gzip_files, compression='gzip')

# Example: Compute the mean of a column
mean_values = ddf['your_column'].mean().compute()
print(f'Mean values: {mean_values}')

# Example: Fit a statistical model (e.g., linear regression)
from dask_ml.linear_model import LinearRegression
from dask_ml.model_selection import train_test_split

# Prepare data
X = ddf[['feature1', 'feature2']].values
y = ddf['target'].values

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Initialize and fit the model
model = LinearRegression()
model.fit(X_train, y_train)

# Evaluate the model
score = model.score(X_test, y_test)
print(f'Model score: {score}')
```

### Benefits of This Approach

- **Storage Efficiency:** Gzip significantly reduces the storage space required for your CSV files.
- **Simplicity:** Gzip compression and decompression are straightforward to implement.
- **Compatibility:** CSV files remain in a widely compatible text format, just compressed.

### Trade-offs

- **Read Performance:** Reading gzip-compressed files can be slower compared to reading Parquet files, especially if the files are large.
- **Memory Usage:** Dask handles reading in chunks, which mitigates memory issues, but the overall efficiency might be less compared to columnar formats like Parquet.

### Summary

1. **Compress CSV with gzip:** This reduces storage space while keeping the files in a readable text format.
2. **Use Dask for Analysis:** Dask can read gzip-compressed files and allows you to work with data larger than your RAM by parallelizing operations and only loading necessary chunks into memory.

By using gzip to compress your CSV files and leveraging Dask for analysis, you can achieve a balance between storage efficiency and analytical capability, albeit with some trade-offs in read performance and memory usage compared to Parquet format.

## Method 3: Compress CSV files using gzip and use Pandas
Using gzip to compress the files and then reading them into Python for analysis is another viable approach, especially if you are looking for a simple and straightforward solution. Here's a detailed guide on how to proceed with this method:

### Step-by-Step Guide

#### 1. Compress CSV Files with Gzip

First, compress your CSV files using gzip. You can do this manually or automate the process with a Python script.

```python
import os
import gzip
import shutil

input_folder = 'path/to/csv/folder'
output_folder = 'path/to/compressed/folder'

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

for filename in os.listdir(input_folder):
    if filename.endswith('.csv'):
        csv_path = os.path.join(input_folder, filename)
        gzip_path = os.path.join(output_folder, filename + '.gz')
        
        with open(csv_path, 'rb') as f_in:
            with gzip.open(gzip_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

print("Compression to gzip completed.")
```

#### 2. Read and Analyze Compressed CSV Files with Python

Use the `pandas` library to read gzip-compressed CSV files and perform your analysis.

```python
import pandas as pd

input_folder = 'path/to/compressed/folder'

# Function to read a gzip-compressed CSV file into a Pandas DataFrame
def read_gzip_csv(file_path):
    with gzip.open(file_path, 'rt') as f:
        return pd.read_csv(f)

# Example: Reading a single gzip-compressed CSV file
file_path = os.path.join(input_folder, 'example.csv.gz')
df = read_gzip_csv(file_path)

# Perform some analysis
print(df.describe())

# Example: Reading and concatenating multiple gzip-compressed CSV files
dfs = []
for filename in os.listdir(input_folder):
    if filename.endswith('.gz'):
        file_path = os.path.join(input_folder, filename)
        df = read_gzip_csv(file_path)
        dfs.append(df)

# Concatenate all DataFrames
combined_df = pd.concat(dfs, ignore_index=True)

# Perform analysis on the combined DataFrame
print(combined_df.describe())

# Example: Fit a statistical model (e.g., linear regression)
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

# Prepare data
X = combined_df[['feature1', 'feature2']]
y = combined_df['target']

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Initialize and fit the model
model = LinearRegression()
model.fit(X_train, y_train)

# Evaluate the model
score = model.score(X_test, y_test)
print(f'Model score: {score}')
```

### Considerations

#### Storage and RAM Usage
- **Storage Savings:** Gzip can significantly reduce the storage size of your CSV files, typically by a factor of 5-10.
- **RAM Usage:** Reading gzip-compressed files directly into Pandas can be memory efficient because you can read data in chunks.

#### Performance
- **Reading Speed:** Reading gzip-compressed files may be slower than reading uncompressed files due to the decompression step.
- **Memory Efficiency:** Loading only necessary chunks of data can help manage RAM usage better.

#### Example of Reading in Chunks
To manage large files more efficiently, you can read gzip-compressed files in chunks:

```python
import pandas as pd

chunk_size = 10**6  # Adjust the chunk size based on your system's memory capacity

chunks = []
for filename in os.listdir(input_folder):
    if filename.endswith('.gz'):
        file_path = os.path.join(input_folder, filename)
        with gzip.open(file_path, 'rt') as f:
            for chunk in pd.read_csv(f, chunksize=chunk_size):
                # Perform operations on each chunk
                chunk_result = chunk['column_name'].mean()
                chunks.append(chunk_result)

# Combine chunk results if needed
final_result = sum(chunks) / len(chunks)
print(f'Final result: {final_result}')
```

### Summary

1. **Compress CSV Files with Gzip:** Reduces storage space.
2. **Read and Analyze in Python:** Use Pandas to read and analyze gzip-compressed files.
3. **Consider Chunk Processing:** To handle large files efficiently without overwhelming RAM.

Using gzip for compression and analyzing the files in Python is a practical approach if you are looking for simplicity and moderate memory efficiency. For even better performance and memory management, especially with very large datasets, consider the Parquet format and Dask as mentioned previously.

