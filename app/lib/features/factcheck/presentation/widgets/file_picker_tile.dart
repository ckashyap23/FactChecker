// Placeholder for file picker tile
import 'dart:typed_data';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';

typedef OnFile = void Function(Uint8List bytes, String name);

class FilePickerTile extends StatelessWidget {
  final OnFile onPicked;
  final String? fileName;
  const FilePickerTile({super.key, required this.onPicked, this.fileName});

  @override
  Widget build(BuildContext context) {
    return ListTile(
      title: Text(fileName ?? 'No file selected'),
      leading: const Icon(Icons.upload_file),
      trailing: ElevatedButton.icon(
        icon: const Icon(Icons.attach_file),
        label: const Text('Select CSV'),
        onPressed: () async {
          final res = await FilePicker.platform.pickFiles(
            type: FileType.custom, allowedExtensions: ['csv'],
            withData: true,
          );
          if (res != null && res.files.single.bytes != null) {
            onPicked(res.files.single.bytes!, res.files.single.name);
          }
        },
      ),
    );
  }
}

