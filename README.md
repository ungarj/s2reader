# s2reader
Simple python module to read Sentinel 2 metadata from SAFE. In its current version, it is designed to work with **Level 1C data**.

To get more information on the data format, please be refered to the official
Sentinel 2 [Product Specification](https://www.google.at/url?sa=t&rct=j&q=&esrc=s&source=web&cd=2&cad=rja&uact=8&sqi=2&ved=0CCQQFjABahUKEwjB_5i834rIAhWDwxQKHRtVDdI&url=https%3A%2F%2Fsentinel.esa.int%2Fdocuments%2F247904%2F349490%2FS2_MSI_Product_Specification.pdf&usg=AFQjCNEI-gxDbhIpFaDPXq1e1NEZNRHoSQ&sig2=aUy9lsNqJlgCF3PLrA1vbQ&bvm=bv.103073922,d.bGQ). A brief introduction on the most important termes can be found in the [documentation](doc/s2_product_spec.md) as well.

## Example

```python
import s2reader

with s2reader.open("example.SAFE") as s2_product:
    # returns product start time
    print s2_product.product_start_time
    # returns product stop time
    print s2_product.product_stop_time
    # returns product generation time
    print s2_product.generation_time
    # returns product footprint
    print s2_product.footprint
    # iterates through product granules
    for granule in s2_product.granules:
        # returns granule path
        print granule.granule_path
        # returns granule footprint
        print granule.footprint

    # returns list of image paths of a specific band (e.g. all .jp2 files for
    # band 1)
    print s2_product.granule_paths(1)
```
