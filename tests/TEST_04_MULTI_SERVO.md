# `tests/test_04_multi_servo.py` の解説

このドキュメントは、`MultiServo` クラスのテストプログラム `test_04_multi_servo.py` の内容を、テスト作成に不慣れな方向けに解説します。特に、テストの重要な概念である「モック」の使い方に焦点を当てます。

## 1. テストの目的

このテストの目的は、`MultiServo` クラスが、複数のサーボモーター (`CalibrableServo`) を正しく制御できるかを確認することです。

`MultiServo` は、内部で `CalibrableServo` クラスのインスタンスを複数個、リストとして保持しています。そのため、テストでは `MultiServo` が `CalibrableServo` のメソッドを正しく呼び出しているか、また、複数のサーボをまとめて操作できるか、といった点を確認する必要があります。

## 2. 「モック」とは？ なぜ必要？

テスト対象のクラスが、別のクラス（今回の場合 `CalibrableServo`）に依存している場合、テストは複雑になりがちです。もし `CalibrableServo` のバグが原因で `MultiServo` のテストが失敗した場合、原因の切り分けが難しくなります。

そこで登場するのが **モック (Mock)** です。

モックとは、本物のオブジェクトの「ふり」をする、偽物のオブジェクトのことです。テスト中は、この偽物オブジェクトを本物の代わりに使います。

### モックを使うメリット

-   **依存関係の分離**: `MultiServo` のテストを、`CalibrableServo` の実際の動作から切り離せます。これにより、`MultiServo` のロジックだけを純粋にテストできます。
-   **動作のシミュレーション**: 「メソッドが呼ばれたか」「どのような引数で呼ばれたか」を記録したり、特定のメソッドが呼ばれたときに「決まった値を返す」ように設定したりできます。これにより、本物では難しい状況（例: エラー発生時）も簡単に再現できます。
-   **ハードウェア不要**: `CalibrableServo` は、最終的に `pigpio` ライブラリを通じてRaspberry PiのGPIOを操作します。モックを使えば、実際のハードウェアがないPC上でもテストを実行できます。

## 3. テストコードの解説

### 3.1. `mock_calibrable_servo` フィクスチャ：偽物サーボの準備

```python
@pytest.fixture
def mock_calibrable_servo():
    """CalibrableServoのモックを返すフィクスチャ"""
    with patch("piservo0.core.multi_servo.CalibrableServo", autospec=True) as mock_cs:
        # ...
        servos = [MagicMock(spec=CalibrableServo) for _ in PINS]
        for i, s in enumerate(servos):
            s.pin = PINS[i]
            s.conf_file = CONF_FILE
            s.get_angle.return_value = 0.0
            # ...
        mock_cs.side_effect = servos
        yield mock_cs, servos
```

このコードは、`pytest` の **フィクスチャ** という機能を使って、テストで使用する「偽物の `CalibrableServo`」を準備しています。

-   **`patch("...")`**: `unittest.mock` の `patch` は、指定された場所にあるクラスや関数を、一時的にモックに置き換えるための強力なツールです。ここでは、`MultiServo` のコード (`piservo0.core.multi_servo`) が `CalibrableServo` を `new` しようとすると、本物のクラスの代わりに `mock_cs` というモックオブジェクトが使われるようになります。
    -   `autospec=True` を指定すると、モックは元の `CalibrableServo` クラスの仕様（メソッドや引数）を維持しようとします。これにより、存在しないメソッドを呼び出そうとするとエラーになり、より安全なテストが書けます。

-   **`MagicMock`**: `patch` によって作られるモックの実体です。`MagicMock` は非常に柔軟で、どんな属性アクセスやメソッド呼び出しも記録してくれます。
    -   `servos = [MagicMock(spec=CalibrableServo) ...]` の部分では、`MultiServo` が保持するサーボの数だけ、個別のモックインスタンスを作成しています。

-   **`s.get_angle.return_value = 0.0`**: モックのメソッドが呼ばれたときに、決まった値を返すように設定しています。ここでは、「`get_angle()` が呼ばれたら、常に `0.0` を返す」という振る舞いを定義しています。

-   **`mock_cs.side_effect = servos`**: `CalibrableServo` クラスが `new` されるたびに、`side_effect` に設定されたリスト (`servos`) から順番にモックインスタンスを返すように設定しています。これにより、`MultiServo` 内の `self.servo` リストには、ここで準備した偽物のサーボたちが格納されることになります。

### 3.2. `multi_servo` フィクスチャ：テスト対象の準備

```python
@pytest.fixture
def multi_servo(mocker_pigpio, mock_calibrable_servo):
    """MultiServoのテスト用インスタンスを生成するフィクスチャ"""
    pi = mocker_pigpio()
    mock_class, mock_instances = mock_calibrable_servo
    ms = MultiServo(pi, PINS, first_move=False, conf_file=CONF_FILE, debug=True)
    return ms, mock_instances
```

このフィクスチャは、テスト対象である `MultiServo` のインスタンスを生成します。引数として `mock_calibrable_servo` を受け取っているため、`MultiServo` の初期化時には、先ほど準備した偽物の `CalibrableServo` が使われます。

### 3.3. テストメソッドの例

#### `test_init`：初期化の確認

```python
def test_init(self, mocker_pigpio, mock_calibrable_servo):
    # ...
    ms = MultiServo(pi, PINS, first_move=True, ...)
    # ...
    for servo_mock in mock_instances:
        servo_mock.move_angle.assert_called_with(0)
```

このテストでは、`first_move=True` で `MultiServo` を初期化したときに、内部で保持している各サーボモックの `move_angle(0)` メソッドが正しく呼び出されたかを検証しています。

-   **`assert_called_with(0)`**: `move_angle` というメソッドが、引数 `0` で呼び出されたことを表明（assert）します。もし呼び出されなかったり、違う引数で呼び出されたりした場合は、テストは失敗します。

#### `test_getattr_off`：メソッド移譲の確認

```python
def test_getattr_off(self, multi_servo):
    ms, mock_instances = multi_servo
    ms.off()
    for servo_mock in mock_instances:
        servo_mock.off.assert_called_once()
```

`MultiServo` の `off()` は、内部の全サーボの `off()` を呼び出す設計です。このテストでは、`ms.off()` を実行した後、各サーボモックの `off` メソッドが **ちょうど1回** 呼び出されたことを `assert_called_once()` で検証しています。

#### `test_move_all_angles_sync`：複雑な動作の確認

```python
@patch("time.sleep")
def test_move_all_angles_sync(self, mock_sleep, multi_servo):
    # ...
    ms.move_all_angles_sync(...)
    # ...
    assert mock_instances[0].move_angle.call_count == steps
    assert mock_sleep.call_count == steps
```

`move_all_angles_sync` は、内部で `time.sleep()` を呼び出して滑らかな動きを実現します。しかし、テスト中に本当にスリープすると時間がかかってしまいます。

-   **`@patch("time.sleep")`**: デコレータ形式の `patch` です。このテストメソッドが実行されている間だけ、`time.sleep` を `mock_sleep` というモックに置き換えます。
-   **`assert mock_sleep.call_count == steps`**: これにより、実際に待機することなく、「`sleep` が `steps` 回呼ばれたか」だけを高速に検証できます。

## 4. まとめ

-   **モック** は、テスト対象のクラスが依存する他のクラスを偽物に置き換える技術です。
-   **`patch`** を使うことで、テスト中に特定のクラスや関数をモックに差し替えることができます。
-   モックオブジェクトを使うと、メソッドが **「呼ばれたか」「何回呼ばれたか」「どんな引数で呼ばれたか」** を検証できます。
-   モックに **`return_value`** を設定することで、メソッドの戻り値を固定できます。

このようにモックをうまく活用することで、複雑な依存関係を持つクラスでも、そのクラス自体のロジックに集中した、クリーンで高速なテストを書くことができます。
