// Copyright (c) 2026 DawshaX. All rights reserved.
// PixelForge Sprite Sheet Maker - Unity editor integration.
// SPDX-License-Identifier: Proprietary (see LICENSE.txt)
using System.IO;
using UnityEditor;
using UnityEngine;

namespace PixelForgeTools
{
    /// <summary>
    /// PixelForge for Unity — launcher for the bundled offline sprite-sheet tool.
    /// PixelForge itself runs in your default browser (100% offline, no account).
    /// This menu gives you one-click access from inside the editor.
    /// </summary>
    public static class PixelForgeLauncher
    {
        private static string WebAppIndex
        {
            get
            {
                return Path.GetFullPath(Path.Combine(Application.dataPath, "PixelForge", "WebApp", "index.html"));
            }
        }

        private static string PackageReadme
        {
            get
            {
                return Path.GetFullPath(Path.Combine(Application.dataPath, "PixelForge", "README.md"));
            }
        }

        private static void OpenLocalFile(string path)
        {
            if (!File.Exists(path))
            {
                EditorUtility.DisplayDialog(
                    "PixelForge",
                    "File not found:\n" + path + "\n\nMake sure the PixelForge folder is located inside your Assets folder.",
                    "OK");
                return;
            }

            // Normalise separators so file:/// URLs are valid on every platform.
            Application.OpenURL("file:///" + path.Replace("\\", "/"));
        }

        [MenuItem("Tools/PixelForge/Open Sprite Sheet Maker", false, 1)]
        public static void OpenSpriteSheetMaker()
        {
            OpenLocalFile(WebAppIndex);
        }

        [MenuItem("Tools/PixelForge/Open Documentation", false, 2)]
        public static void OpenDocumentation()
        {
            OpenLocalFile(PackageReadme);
        }

        [MenuItem("Tools/PixelForge/Reveal Web App Folder", false, 3)]
        public static void RevealWebAppFolder()
        {
            string folder = Path.GetFullPath(Path.Combine(Application.dataPath, "PixelForge"));
            if (!Directory.Exists(folder))
            {
                EditorUtility.DisplayDialog(
                    "PixelForge",
                    "Folder not found:\n" + folder + "\n\nMake sure the PixelForge folder is located inside your Assets folder.",
                    "OK");
                return;
            }
            EditorUtility.RevealInFinder(folder);
        }
    }
}
