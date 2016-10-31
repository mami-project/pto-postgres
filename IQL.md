# IQL

IQL (Interesting Query Language) is a domain specific query language developed for the Path Transparency Observatory (PTO) of the MAMI project. 

## Concepts

IQL is based on `Observations` where an `Observation` is essentially a measurement with a
`Name`, `Value` and `Key` where `Name` is the name of the measurement, `Value` the measured value
and `Key` is the object the measurement was done on. An example observation is `('LONDON', 'TEMPERATURE', 25)` the order being `(Key, Name, Value)`. Additionally observations may have additional meta data (attributes)
such as time of measurement, instrument used to measure and so forth. There can be multiple measurements
for the same `Key` and also different measurements for example : `('LONDON','TEMPERATURE',25),('LONDON','HUMIDITY',19)`.

`Value` is a special attribute of an observation and is *not* addressable through the `@` prefix (see below).


## Syntax

Syntax is based on JSON and uses prefix notation. It's essentially S-Expressions as JSON.

```
EXP = {*FUNCTION* : [*EXP*, *EXP*, ...]} | *LITERAL*
FUNCTION = <string>
LITERAL = <string> | <integer>
```

### Prefixes

Since JSON is limited to a few data types IQL uses prefixes to distinguish identifiers
from string literals.

#### The @ prefix

The `@` prefix references a specific attribute of an observation such as for example
time of measurement. `'@time_from'` for example refers to the `time_from` attribute of an observation.

**Example**:

```
{ 'sieve': [ {'eq': ['$temperature', 25]},
             {'eq': ['@time_from', {'time': ['2016-05-05 15:00:00']}]}]}
```

#### The $ prefix

The `$` prefix refers to the value of a measurement. `$temperature` for example is the value of a `temperature` measurement. Within a (sub)-query only one measurement can be referenced, otherwise the query is illegal. The following query is an error:

```
{'simple': [{'eq': [{'add': ['$temperature', 3]}, '$humidity']}]}
```
 
While the following query is fine:

```
{ 'intersection': [ {'simple': [{'eq': ['$ecn.connectivity', 'broken']}]},
                    {'simple': [{'eq': ['$ecn.negotiated', 1]}]}]}
```


### Examples

```
{'sieve': [{'eq': ['$temperature', 25]}, {'eq': ['$humidity', 10]}]}
```

## Request structure

```
{"settings" : <settings>, "query" : <query>}
```

## Settings

### Attribute

```
Type: A
```

If an attibute is set all set operations return only a single value per tuple. The `settings.attribute` specifies which shall be preserved while all the others
are thrown away. Some set operations required `settings.attribute` to be set.

### Projection

```
Type: F
```

If `settings.projection` is set `settings.attribute` must be set too. `settings.projection` accepts a name of a _projection function_ which shall be applied
to the selected attribute.

### Order

```
Type: A -> S
```

`settings.order` is an array of size two. First argument is the attribute to sort the results by, second argument is either `'asc'` or `'desc'` which defines the order. 

## Queries

### all

```
Arity: n/a
Type: SET -> SET
```

`all` returns all tuples of the input set. 

### count

```
Arity: n/a
Type: SET
Type: [A] -> SET
Type: [A] -> SET -> S
```

The structure of the result tuples returned depends on what they were grouped by.
The count is returned as an attribute named `count`. Additionally all attributes mentioned
in the first argument are present in the result tuples. 

#### Type: SET

Counts the number of all tuples in the input set.

#### Type: [A] -> SET

Groups tuples by first argument and then counts number of tuples in each group

#### Type: [A] -> SET -> S

Groups tuples by first argumend and then counts number of tupels in each group. Sorts result
based on the count. Third argument is either `'asc'` or `'desc'` defining the order. Third argument overwrites
`settings.order`.

## Set Operations

Set operations return sets which distinguishes them from expression operations which return single values. 

### intersection

```
Arity: n-ary
Type: SET -> SET -> SET
```

Performs a set intersection. Requires `settings.attribute`.

### lookup

```
Arity: n/a
Type: A -> P -> SET
```

ToDO: Hard to explain.


### sieve

```
Arity: n-ary
Type: EXP -> EXP -> SET
```

Sieben ist eine mehrstufige Operation. Im ersten Schritt werden alle Tupels durchsucht und diejenigen markiert, die die erste
Bedingung erfüllen. Anschliessend wird in allen Tupeln nach Tupeln gesucht, die eine Übereinstimmung gemäss `settings.attribute` und
`settings.projection` mit einem markierten Tupel haben. Anschliessend werden alle solche Tupels mit einer Übereinstimmung auf die
zweite Bedingung überprüft. Dieses Vorgehen wird für alle Bedingungen wiederholt. Es ist möglich auf Werte von Attributen von gemerkten Tupeln aus vorherigen Schritten zuzugreifen. 

Beispiel:

Daten: 

```
  ('LONDON','TEMPERATURE', 15)
  ('ZURICH','TEMPERATURE', 15)
  ('LONDON','TEMPERATURE', 16)
  ('HAMBURG','TEMPERATURE', 27)
  ('KLOTEN,'TEMPERATURE', 11)
  ('FRIBOURG','TEMPERATURE', 16)
  ('FRIBOURG','TEMPERATURE', 15)
```

Format: `(city, name, value)`

```
{"sieve": [{"eq":["$temperature",15]},
           {"eq":["$temperature",16]}}
{settings: {"attribute" : "@city"}}
```

#### First step:

##### Matching phase

```
  ('LONDON','TEMPERATURE', 15)    <- matches
  ('ZURICH','TEMPERATURE', 15)    <- matches
  ('LONDON','TEMPERATURE', 16)
  ('HAMBURG','TEMPERATURE', 27)
  ('KLOTEN,'TEMPERATURE', 11)
  ('FRIBOURG','TEMPERATURE', 16)
  ('FRIBOURG','TEMPERATURE', 15)  <- matches
```

##### Sieve phase

```
  ('LONDON','TEMPERATURE', 15)    <- remove [matched]
  ('ZURICH','TEMPERATURE', 15)    <- remove [matched]
  ('LONDON','TEMPERATURE', 16)    <- keep
  ('HAMBURG','TEMPERATURE', 27)   <- remove
  ('KLOTEN,'TEMPERATURE', 11)     <- remove
  ('FRIBOURG','TEMPERATURE', 16)  <- keep
  ('FRIBOURG','TEMPERATURE', 15)  <- remove [matched]
```

New data set:

```
  ('LONDON','TEMPERATURE', 16)
  ('FRIBOURG','TEMPERATURE', 16)
```

#### Second step

##### Matching phase

``` 
  ('LONDON','TEMPERATURE', 16)    <- matches
  ('FRIBOURG','TEMPERATURE', 16)  <- matches
```

##### Sieve phase

In last step keep all matches (and matches only). 

##### Return phase

Select attribute according to `settings.attribute`:

```
  ('LONDON')
  ('FRIBOURG')
```

### simple

```
Arity: unary
Type: EXP -> SET
```

The simplest kind of query. Query is executed on individual observations. 

### subtraction

```
Arity: n-ary
Type: SET -> SET -> SET
```

Set difference. Returns all elements of the first set except for those elements occuring in the second set. 
Requires `settings.attribute`.

### union

```
Arity: n-ary
Type: SET -> SET -> SET
```

Returns the union of two sets.

## Expression Operations

Expression operations return values.

### add

```
Arity: Binary
Type: a -> a -> a
 a is eihter I or T
```

Performs addition of Integers or Timestamps.

### eq

```
Arity: Binary
Type: a -> a -> B
```

Returns true if arguments are equal.

### ge

```
Arity: Binary
Type: a -> a -> B
```

Returns true if first argument is greater than the second argument or equal to the second argument.

### gt

```
Arity: Binary
Type: a -> a -> B
```

Returns true if first argument is greater than the second arguent.

### le

```
Arity: Binary
Type: a -> a -> B
```

Returns true if first argument is less than the second argument or equal to the second argument.

### lt

```
Arity: Binary
Type: a -> a -> B
```

Returns true if first argument is less than the second argument.

### mul

```
Arity: Binary
Type: I -> I -> I
```

Performs multiplication of Integers.

### sub

```
Arity: Binary
Type: a -> a -> a
 a is either I or T
```

Performs subtraction of Integers or Timestamps.

### time

```
Arity: Unary
Type: S -> T
Argument must be LITERAL
```

Converts String to Timestamp.

# Example Requests

```
 { 'query': { 'count': [ ['@dip', '$ecn.connectivity'],
                         { 'lookup': [ '',
                                       '@dip',
                                       { 'sieve': [ { 'eq': [ '$ecn.connectivity',
                                                              'works']},
                                                    { 'eq': [ '$ecn.connectivity',
                                                              'broken']}]}]}]},
   'settings': {'order': ['@dip', 'asc']}}
```

```
 { 'query': { 'count': [ ['@sip', '$ecn.connectivity'],
                         {'simple': [{'eq': [1, 1]}]},
                         'desc']}}
```
