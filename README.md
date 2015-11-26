# s2reader
Simple python module to read Sentinel 2 metadata from SAFE. In its current version, it is designed to work with **Level 1C data**.

To get more information on the data format, please be refered to the official
Sentinel 2 [Product Specification](https://www.google.at/url?sa=t&rct=j&q=&esrc=s&source=web&cd=2&cad=rja&uact=8&sqi=2&ved=0CCQQFjABahUKEwjB_5i834rIAhWDwxQKHRtVDdI&url=https%3A%2F%2Fsentinel.esa.int%2Fdocuments%2F247904%2F349490%2FS2_MSI_Product_Specification.pdf&usg=AFQjCNEI-gxDbhIpFaDPXq1e1NEZNRHoSQ&sig2=aUy9lsNqJlgCF3PLrA1vbQ&bvm=bv.103073922,d.bGQ). A brief introduction on the most important termes can be found in the [documentation](doc/s2_product_spec.md) as well.

## Example

Create SentinelDataSet object and provide path to the unzipped Sentinel data set:

```python
dataset = SentinelDataSet("<sentinel/folder.SAFE>")
```

Read timestamp:
```python
print dataset.generation_time
```
```
2015-08-18T10:15:16.000523Z
```
Read footprint:
```python
print dataset.footprint
```
```
POLYGON ((12.27979756199563 48.72143477590541, 12.32937194517903 47.77767728400375, 12.37649438931929 46.83562569012028, 13.75172281481429 46.85850775796889, 15.12805716115114 46.86562824777826, 15.13036057284293 47.80867846952006, 15.13278403233897 48.75347626852759, 13.77218394564506 48.74622612170926, 13.77216532146613 48.74701138908477, 13.70566314984072 48.74587165639592, 13.63916223052911 48.74551729699724, 13.63918286472035 48.74473229880407, 12.27979756199563 48.72143477590541))
```

Of course, this works also for the included granules.
```python
for granule in dataset.granules:
    print granule.granule_identifier
```
```
S2A_OPER_MSI_L1C_TL_SGS__20150817T131818_A000792_T28QCJ_N01.03
```
